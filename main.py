import os
import sys
import argparse

parser = argparse.ArgumentParser(description="Embed a message in a JPEG file")
parser.add_argument("-l", "--lower-bits", type=int, choices=[1, 2, 3], default=1,
                    help="Number of least significant bits used to embed the message", dest="n_lower_bits")
parser.add_argument("-i", "--image-file", type=str, required=True,
                    help="JPEG image in which the message will be embedded", dest="input_file")
parser.add_argument("-o", "--output-name", type=str, required=True,
                    help="Name of the output file with the embedded message", dest="output_file")
parser.add_argument("-e", "--embed-message", type=str, required=True, dest="embed_message")
args = parser.parse_args()


def seek_txt():
    fname = "testfiles/file.txt"
    # file needs to be opened in b mode in order to do negative searches
    with open(fname, "rb") as f:
        # Set pointer to the beginning of the file (starting from b0 with 0 bytes offset)
        print("offset: %s" % f.tell())
        # readline() automatically moves the file pointer for the offset until 0x0d0a is discovered in the file
        # readline() advances from the current file handler offset as long as it discovers a \r\n or \n and then
        # returns the read text
        print("readline: %s, offset: %d" % (f.readline(), f.tell()))
        # will tell b20 (actual content (16b) + \r\n (2b, 0x0d0a) for text files
        # b44 = 20b + length of new line (21b) + 0x0d0a (2b)
        # offset pointer needs to be set AFTER the last byte that should be read, because it will be "consumed"
        # example: b20 offset means that the pointer is set after the 20th bytes (so all previous 20 bytes are read)
        print("readline: %s, offset: %d" % (f.readline(), f.tell()))
        # move b10
        f.seek(-10, os.SEEK_CUR)
        # move 10 bytes back from the current pos and read until the end of line (\r\n)
        print("readline: %s, offset: %d" % (f.readline(), f.tell()))
        # move 10 bytes back from the current pos and read only the first 2 bytes
        f.seek(-10, os.SEEK_CUR)
        print("readline: %s, offset: %d" % (f.read(2), f.tell()))
        f.close()


def checks():
    with open(fname, "rb") as f:
        f.seek(0, os.SEEK_SET)
        hdr_soi = f.read(2)
        if int(hdr_soi.hex(), 16) != 65496:  # 0xffd8
            print("Error: not a JPEG file...")
            sys.exit(0)
        print("size: %d" % os.path.getsize(fname))
        print("{0:#x}\thdr_soi: {1:#x}".format(f.tell(), int(hdr_soi.hex(), 16)))
        hdr_app0 = f.read(2)
        print("{0:#x}\thdr_app0: {1:#x}".format(f.tell(), int(hdr_app0.hex(), 16)))
        hdr_app0_length = f.read(2)
        print("{0:#x}\thdr_app0_length: {1:#x}".format(f.tell(), int(hdr_app0_length.hex(), 16)))
        hdr_ident = f.read(5)
        print("{0:#x}\thdr_ident: {1:#x}".format(f.tell(), int(hdr_ident.hex(), 16)))
        hdr_ver = f.read(2)
        print("{0:#x}\thdr_ver: {1:#x}".format(f.tell(), int(hdr_ver.hex(), 16)))
        hdr_units = f.read(1)
        print("{0:#x}\thdr_units: {1:#x}".format(f.tell(), int(hdr_units.hex(), 16)))
        hdr_xdensity = f.read(2)
        print("{0:#x}\thdr_xdensity: {1:#x}".format(f.tell(), int(hdr_xdensity.hex(), 16)))
        hdr_ydensity = f.read(2)
        print("{0:#x}\thdr_ydensity: {1:#x}".format(f.tell(), int(hdr_ydensity.hex(), 16)))
        hdr_xthumb = f.read(1)
        print("{0:#x}\thdr_xthumb: {1:#x}".format(f.tell(), int(hdr_xthumb.hex(), 16)))
        hdr_ythumb = f.read(1)
        print("{0:#x}\thdr_ythumb: {1:#x}".format(f.tell(), int(hdr_ythumb.hex(), 16)))

        # Check if the string to embed can fit into the image
        global bit_list
        bit_list = text_to_bits(args.embed_message)
        # message embedding starts at 0x1500
        # required space calculation: len(bit_list) % n_lower_bits + (floor(len(bit_list) / n_lower_bits))
        required_space = len(bit_list)


def embed_str_in_img(s):
    with open(fname, "rb") as f:
        bit_list = text_to_bits(s)
        # [3:5] -> exklusiv 5, also index 3 und 4 wird nur zurückgegeben
        # [:3] -> bis index 3, also 0, 1, 2
        # untere grenze inklusiv, obere grenze exlusiv
        # bit_l_s = [str(x) for x in bit_list]
        # print("".join(bit_l_s[:3]))
        # print(int("".join(bit_l_s[:4]), 2))
        # print(int(bit_list[3:5], 2))


def text_to_bits(text):
    bits = bin(int.from_bytes(text.encode(), 'big'))[2:]
    return list(map(int, bits.zfill(8 * ((len(bits) + 7) // 8))))


def text_from_bits(bits):
    n = int(''.join(map(str, bits)), 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()


if __name__ == '__main__':
    global fname, bit_list
    fname = args.input_file
    checks()
    embed_str_in_img(sys.argv[2])
