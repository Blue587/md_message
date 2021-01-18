import csv, sys, re, os, ndspy.rom

print("argument 1: input executable file path (decompressed arm9.bin for Shiren4 and Shiren5, f5psp.prx for Shiren4+, eboot.bin for Shiren5+) or DS ROM file path (for Shiren4 and Shiren5)")
print("argument 2: name of the game")

mult = 1
# add 64-bit support when Shiren5p releases on Switch

input_file = open(sys.argv[1], "rb")

if sys.argv[3] == "ds" and sys.argv[1][-4:] == ".nds" or sys.argv[1][-4:] == ".srl":
    rom = ndspy.rom.NintendoDSRom(input_file.read())
    arm9 = rom.loadArm9()
    rom.arm9 = arm9.save()
    fullpath = sys.argv[1].split("/")
    filename = fullpath[-1]
    os.makedirs("decompressed_arm9", exist_ok=True)
    with open("decompressed_arm9/" + filename[:-4] + "_arm9.bin", "wb") as arm9_file:
        arm9_file.write(rom.arm9)
    input_file.close()
    print("decompressed_arm9/" + filename[:-4] + "_arm9.bin was created.\n")
    input_file = open("decompressed_arm9/" + filename[:-4] + "_arm9.bin", "rb")

print("What do you want to do?")
print("1) Use preset data")
print("2) Enter the data manually")
print("3) Quit")
choice = input()

if choice == "3":
    quit()

elif choice == "1":
    print("Which preset data do you want to use?")
    print("1) shiren4-jp")
    print("2) shiren5-jp")
    print("3) shiren4p-jp-psp")
    print("4) shiren5p-en-psv")
    choice_preset = input()

    if choice_preset == "1" or choice_preset == "shiren4-jp":
        start_address = 0xc33e8
        end_of_text_address = 0xc3b65
        data_address = 0xa95f4
        difference = -0x2000000
        amount_of_entries = 147

    elif choice_preset == "2" or choice_preset == "shiren5-jp":
        start_address = 0xdd8c8
        end_of_text_address = 0xde199
        data_address = 0xb8dfc
        difference = -0x2000000
        amount_of_entries = 159

    elif choice_preset == "3" or choice_preset == "shiren4p-jp-psp":
        start_address = 0x3ab5e4
        end_of_text_address = 0x3abdcd
        data_address = 0x3abdd0
        difference = 0xa0
        amount_of_entries = 147

    elif choice_preset == "4" or choice_preset == "shiren5p-en-psv":
        start_address = 0x35e82c
        end_of_text_address = 0x35f0ad
        data_address = 0x35f0b0
        difference = -0x80fff460
        amount_of_entries = 159

elif choice == "2":
    print("Enter the starting address of the first string: ", end="")
    start_address = int(input(), 16)
    print("Enter the address of the last byte of the last string of text: ", end="")
    end_of_text_address = int(input(), 16)
    print("Enter the starting address of the data segment: ", end="")
    data_address = int(input(), 16)
    print("Enter the difference between the addresses of the file and the pointers inside the file (can be negative): ", end="")
    difference = int(input(), 16)
    print("Enter the amount of string/entries the code_table area has (in decimal): ", end="")
    amount_of_entries = int(input())

input_file.seek(start_address)
length_of_text = end_of_text_address - start_address

input_file.seek(start_address)
text = input_file.read(length_of_text)

input_file.seek(data_address)

# code to get all control characters and their strings
data = []
current_address = data_address

for x in range(amount_of_entries):
    input_file.seek(current_address) # sets the address to the data

    string_address = int.from_bytes(input_file.read(0x4 * mult), byteorder="little")
    old = string_address
    string_address = abs(string_address + difference)
    input_file.seek(string_address) # sets the address to that of the string

    string = "["
    while True:
        current_word = input_file.read(0x2)
        if current_word != b"\x00\x00":
            string += current_word.decode("utf-16-le")
        else:
            string += "]"
            break

    input_file.seek(current_address + 0x4)

    data.append((string, # text
                "{0:#0{1}x}".format(int.from_bytes(input_file.read(0x2), byteorder="little"), 6), # char
                "{0:#0{1}x}".format(int.from_bytes(input_file.read(0x2), byteorder="little"), 6), # flags
                "{0:#0{1}x}".format(int.from_bytes(input_file.read(0x1), byteorder="little"), 4))) # length

    current_address += 0xc

input_file.close()

output_file = open(sys.argv[2] + "_text_directives.csv", "w")
csv_writer = csv.writer(output_file)

csv_writer.writerow(["text", "char", "flags", "length"])

for row in data:
    csv_writer.writerow(row)
print("Done!")
print(data)

output_file.close()
