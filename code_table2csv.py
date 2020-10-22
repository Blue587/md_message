import csv, sys

print("argument 1: input code_table.bin file path")
print("argument 2: name of the game (such as \"rtdx\")")
print("credits to EddyK28 for the original \"Text_Directives_-_PSMD_GTI_RTDX.csv\" file\n")

if sys.argv[2] == "rtdx":
    mult = 2
else:
    mult = 1

input_file = open(sys.argv[1], "rb")

input_file.seek(4 * mult) # SIR0
pointer_offset_list_address = input_file.read(4 * mult)

input_file.seek(int.from_bytes(pointer_offset_list_address, byteorder="little"))
end_of_text_address = input_file.read(4 * mult)
data_address = int.from_bytes(input_file.read(4 * mult), byteorder="little")
length_of_text = int.from_bytes(end_of_text_address, byteorder="little") - 0x10 * mult

input_file.seek(0x10 * mult)
text = b"\x00" + input_file.read(length_of_text)
text = text.split(b"\x00\x00")
text = [x[1:] + b"\x00" for x in text]

if sys.argv[2] == "rtdx":
    del text[len(text)-3:]
else:
    del text[-1]

text = ["[" + x.decode("utf-16-le") + "]" for x in text]

input_file.seek(data_address)

data = []
for x in enumerate(text):
    input_file.seek(4 * mult, 1)
    data.append((text[x[0]], # text
                "{0:#0{1}x}".format(int.from_bytes(input_file.read(0x2), byteorder="little"), 6), # char
                "{0:#0{1}x}".format(int.from_bytes(input_file.read(0x2), byteorder="little"), 6), # flags
                "{0:#0{1}x}".format(int.from_bytes(input_file.read(0x2), byteorder="little"), 6), # length
                "{0:#0{1}x}".format(int.from_bytes(input_file.read(0x2), byteorder="little"), 6))) # unk

input_file.close()


output_file = open(sys.argv[2] + "_text_directives.csv", "w")
csv_writer = csv.writer(output_file)

csv_writer.writerow(["text", "char", "flags", "length", "unk"])

for row in data:
    csv_writer.writerow(row)
print("Done!")

output_file.close()
