import csv, os, sys, io

def get_data(flags, length):
    string = ""
    while length > 0:
        string += ":"

        if flags == "0x0009":
            string += "{0:0{1}x}".format(int.from_bytes(input_file.read(0x4), byteorder="little"),8)
        else:
            string += "{0:0{1}x}".format(int.from_bytes(input_file.read(0x2), byteorder="little"),4)
        length -= 1

    return string

print("this program will convert all the files in the chosen \"message\" folder to text files.")

print("argument 1: path to the input \"message\" folder")
print("argument 2: name of the game (must match the text_directives file name)")
print("argument 3: \"64-bit\" if the platform the game is for uses 64-bit addresses (such as the Switch), can be left blank otherwise")

if len(sys.argv) == 3:
    mult = 1
elif len(sys.argv) == 4 and sys.argv[3] == "64-bit":
    mult = 2

text_directives_csv = open(sys.argv[2] + "_text_directives.csv", "r")
text_directives_reader = csv.reader(text_directives_csv)

text_directives_dict = {}
lengths_dict = {}
flags_dict = {}
unk_dict = {}
for line in text_directives_reader:
    text_directives_dict[line[1]] = line[0]
    flags_dict[line[1]] = line[2]
    lengths_dict[line[1]] = line[3]
    if len(line) == 5:
        unk_dict[line[1]] = line[4]
text_directives_csv.close()

zero_flag_chars = [x for x in text_directives_dict if flags_dict[x] == "0x0000"] # list of text directives that don't include data

fullpath = sys.argv[1].split("/")
folderpath = "/".join(fullpath[:-1]) + "/"
foldername = fullpath[-1]

for filename in os.listdir(folderpath + foldername):
    with open(os.path.join(folderpath + foldername + "/" + filename), "rb") as input_file:

        input_file.seek(4 * mult) # SIR0
        pointer_offset_list_address = input_file.read(4 * mult)
        input_file.seek(int.from_bytes(pointer_offset_list_address, byteorder="little") + 4)
        end_of_text_address = input_file.read(4 * mult) # gets the address of the end of the last string of text
        input_file.seek(int.from_bytes(end_of_text_address, byteorder="little"))
        end_of_text = input_file.tell()

        input_file.seek(0x10 * mult)
        newtext = ""

        while input_file.tell() != end_of_text:
            upper = input_file.read(0x1)
            lower = input_file.read(0x1)
            word = upper + lower
            emptied_word = b"\x00" + lower
            hex_string = "{0:#0{1}x}".format(int.from_bytes(word, byteorder="little"),6)
            emptied_hex_string = "{0:#0{1}x}".format(int.from_bytes(emptied_word, byteorder="little"),6)

            if hex_string in zero_flag_chars:
                newtext += text_directives_dict[hex_string]

            else:
                if hex_string in text_directives_dict:
                    newtext += text_directives_dict[hex_string][:-1]
                    flags = flags_dict[hex_string]
                    length = int(lengths_dict[hex_string], 16)
                    newtext += "{0:0{1}x}".format(int.from_bytes(upper, byteorder="little"),2)
                    newtext += get_data(flags, length) + "]"

                elif emptied_hex_string in text_directives_dict:
                    newtext += text_directives_dict[emptied_hex_string][:-1]
                    flags = flags_dict[emptied_hex_string]
                    length = int(lengths_dict[emptied_hex_string], 16)
                    newtext += "{0:0{1}x}".format(int.from_bytes(upper, byteorder="little"),2)
                    newtext += get_data(flags, length) + "]"

                elif hex_string == "0x0000":
                    newtext += "\n"

                else:
                    newtext += word.decode("utf-16-le")

# to fix: Shiren5 files often have some 0x0002 characters, there is probably a mistake here. not sure about the quotes, commas and the likes.

        os.makedirs(sys.argv[2] + "_" + foldername + "_output", exist_ok=True)
        if filename[-4:] == "dbin":
            outputfile = open(os.getcwd() + "/" + sys.argv[2] + "_" + foldername + "_output/" + filename[:-5] + ".txt", "w", encoding="utf-16-le")
        else:
            outputfile = open(os.getcwd() + "/" + sys.argv[2] + "_" + foldername + "_output/" + filename[:-4] + ".txt", "w", encoding="utf-16-le")
        outputfile.write(newtext)
        outputfile.close()
