import csv, os, sys

print("Tested with Gates to Infinity \"message\" folder files, this will convert all the files in the chosen folder to text files.")

if len(sys.argv) == 1:
    print("Missing argument: path to the input folder")
    print("Missing argument: name of the game")
    quit()

if len(sys.argv) == 2:
    print("Missing argument: name of the game")
    quit()

fullpath = sys.argv[1].split("/")
folderpath = "/".join(fullpath[:-1]) + "/"
foldername = fullpath[-1]

for filename in os.listdir(folderpath + foldername):
    with open(os.path.join(folderpath + foldername + "/" + filename), "rb") as input_file:

        input_file.seek(4) # SIR0
        pointer_offset_list_address = input_file.read(4)
        input_file.seek(int.from_bytes(pointer_offset_list_address, byteorder="little") + 4)
        end_of_text_address = input_file.read(4) # gets the address of the end of the last string of text
        length_of_text = int.from_bytes(end_of_text_address, byteorder="little") - 0x10
        input_file.seek(0x10)
        text = bytearray(input_file.read(length_of_text))

        words_text = []

        mv = memoryview(text).cast("H")
        for x in mv:
            words_text.append(x)

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
            unk_dict[line[1]] = line[4]
        text_directives_csv.close()

        newtext = bytearray()
        value_len = 0
        for index, word in enumerate(words_text):
            hex_number = '{0:0{1}x}'.format(word,4)
            full_char = "0x" + hex_number
            zero_least_significant = "0x" + hex_number[0:2] + "00"

            if value_len > 0:
                newtext += bytearray(str(hex_number), encoding="utf-16-le")
                value_len -= 1
                if value_len == 0:
                    newtext += bytearray(str("]"), encoding="utf-16-le")

                if current_flag == "0x0002" or current_flag == "0x0009":
                    if value_len == 1:
                        newtext += bytearray(":", encoding="utf-16-le")

            else:
                if zero_least_significant in text_directives_dict:
                    current_flag = flags_dict[zero_least_significant]

                    if current_flag == "0x0000":
                        newtext += text_directives_dict[full_char].encode("utf-16-le")

                    if current_flag == "0x0001":
                        newtext += text_directives_dict[zero_least_significant][0:-1].encode("utf-16-le")
                        value_len = int(lengths_dict[zero_least_significant], 16)
                        if value_len == 0:
                            newtext += bytearray(str(hex_number[2:4]) + "]", encoding="utf-16-le")

                    elif current_flag == "0x0002":
                        newtext += text_directives_dict[zero_least_significant][0:-1].encode("utf-16-le")
                        value_len = int(lengths_dict[zero_least_significant], 16) * 2
                        if value_len == 0:
                            newtext += bytearray(str(hex_number[2:4] + "]"), encoding="utf-16-le")

                        else: # what is this used for in this case?
                            newtext += bytearray(str(hex_number[2:4] + ":"), encoding="utf-16-le")

                    elif current_flag == "0x0009":
                        newtext += text_directives_dict[zero_least_significant][0:-1].encode("utf-16-le")
                        value_len = int(lengths_dict[zero_least_significant], 16)
                        if value_len == 0:
                            newtext += bytearray(str(hex_number[2:4] + "]"), encoding="utf-16-le")

                        else: # what is this used for in this case?
                            newtext += bytearray(str(hex_number[2:4] + ":"), encoding="utf-16-le")

                elif hex_number == "0000":
                    newtext += "\n".encode("utf-16-le")

                else:
                    newtext += int(hex_number, 16).to_bytes(2, byteorder="little")

        newtext = newtext.decode("utf-16-le")
        print(newtext)
        os.makedirs(sys.argv[2] + "_" + foldername + "_output", exist_ok=True)
        outputfile = open(os.getcwd() + "/" + sys.argv[2] + "_" + foldername + "_output/" + filename[:-4] + ".txt", "w", encoding="utf-16-le")
        outputfile.write(newtext)
        outputfile.close()
