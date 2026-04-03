import getopt
import os
import sys

from PIL import Image

from constants import *


class Compiler:

    input_dir = ""
    output_dir = ""

    sheet = ""

    def __init__(self, input_dir, output_dir):

        if not output_dir:
            output_dir = input_dir + "_out"

        self.input_dir = input_dir
        self.output_dir = output_dir

        self.sheet = Image.new(
            mode="RGBA",
            size=(int(SHEET_WIDTH), int(SHEET_HEIGHT))
        )

        print(f"reading from {input_dir}, writing to {output_dir}")

        self.process_images()

    def process_images(self):

        files = self.get_image_list()
        output = self.splice_all_images(files)
        # data_map = self.get_data_map(files)
        # print(data_map)

        # output_file = open("file.bin", "wb")
        # output_file.write(binascii.unhexlify(output))
        # output_file.close()

    def get_data_map(self, files):
        x = 0
        y = 0
        increment = 0
        output = ""
        for skin, animations in files.items():
            for anim, direction in animations.items():
                for d, images in direction.items():
                    # output += f'{skin}'
                    # output += f'{anim}'
                    # output += f'{d}'
                    # output += f' images: {len(images)} '
                    # output += f'{64}'
                    # output += f'{64}'
                    for image in images:
                        output += f'{skin} '
                        output += f'{anim} '
                        output += f'{d} '
                        # print(image.split(os.sep)[-1], end="")
                        x = increment % 16
                        y = int(increment / 16)
                        self.put_image(image, x * 64, y * 64, 64, 64)
                        # new_x = x * 64
                        # new_y = y * 64
                        output += f"({x}, {y}, 64, 64)\n"
                        increment += 1

                    # print()
        # print(output, 16)
        return output

    def process_cover(self):
        pass

    def splice_all_images(self, files):

        x = 0
        y = 0
        increment = 0
        output = ""
        output_output = ""
        records = 0
        for skin, animations in files.items():
            for anim, direction in animations.items():
                for d, images in direction.items():
                    records += 1
                    output += f'{skin_encoding.get(skin):0{2}X}'
                    output += f'{animation_encoding.get(anim):0{2}X}'
                    output += f'{direction_encoding.get(d):0{2}X}'
                    output += f'{len(images):0{2}X}'
                    output += f'{64:0{2}X}'
                    output += f'{64:0{2}X}'
                    for image in images:
                        # print(image.split(os.sep)[-1], end="")
                        x = increment % 16
                        y = int(increment / 16)
                        sheet_id = self.put_image(image, x * 64, y * 64, 64, 64)
                        # new_x = x * 64
                        # new_y = y * 64
                        # output += f"{x:0{2}X}{y:0{2}X}"
                        increment += 1
                    print(output)
                    output_output += output
                    output = ""

                        # print()

        print(records)
        print(output_output, 16)
        return output_output

    def get_image_list(self):
        page_path = self.input_dir

        images = {}

        skins = [f.path for f in os.scandir(page_path) if f.is_dir()]

        for skin in skins:
            label = str(skin.split(os.sep)[-1])
            images[label] = {}
            # print("SKIN:" + label)
            animations = [f.path for f in os.scandir(skin) if f.is_dir()]

            for animation in animations:
                images[label][animation.split(os.sep)[-1]] = {}
                # print(animation.split(os.sep)[-1])
                directions = [f.path for f in os.scandir(animation) if f.is_dir()]
                #print("directions: " + ",".join([d.split(os.sep)[-1] for d in directions]))

                for direction in directions:
                    images[label][animation.split(os.sep)[-1]][direction.split(os.sep)[-1]] = sorted([f.path for f in os.scandir(direction) if f.is_file() and f.path.endswith("png")])

        return images
        """
        for _, _, filenames in os.walk(page_path):
            # filenames = [f for f in filenames if not f[0] == "."]
            filenames = [f for f in filenames]
        print(f"got { len(filenames) } pages.")
        filenames = sorted(filenames)
        print(filenames)
        return filenames
        """

    def put_image(self, image_path, x, y, width, height):
        sprite = Image.open(image_path)
        sprite.convert("RGBA")
        sprite.resize((width, height), resample=Image.BILINEAR)
        self.sheet.paste(im=sprite, box=(x, y), mask=sprite)
        self.sheet.save(
            self.output_dir
            + os.sep
            + "spritesheets_1.png"
        )

    def splice_pages(self, spread_number, left_page, right_page):
        left_image = Image.open(self.input_dir + os.sep + "pages" + os.sep + left_page)
        left_image = left_image.convert("RGBA")

        right_image = Image.open(
            self.input_dir + os.sep + "pages" + os.sep + right_page
        )
        right_image = right_image.convert("RGBA")
        left_image = left_image.resize(
            (int(SHEET_WIDTH), int(SHEET_HEIGHT)), resample=Image.BILINEAR
        )
        right_image = right_image.resize(
            (int(SHEET_WIDTH), int(SHEET_HEIGHT)), resample=Image.BILINEAR
        )

        self.sheet.paste(left_image, (0, 0), left_image)
        self.sheet.paste(right_image, (int(SHEET_WIDTH), 0), right_image)

        spread_str = str(spread_number).zfill(3)

        self.sheet.save(
            self.output_dir
            + os.sep
            + "pages"
            + os.sep
            + "spread_"
            + spread_str
            + left_page
        )
        # print(f"saving spread { spread_str } ( { left_page }, { right_page } )")


def main(argv):
    input_dir = ""
    output_dir = ""

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["idir=", "odir="])
    except getopt.GetoptError:
        print("compiler.py -i <input_dir> -o <output_dir>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("compiler.py -i <input_dir> -o <output_dir>")
            sys.exit()
        elif opt in ("-i", "--idir"):
            input_dir = arg
        elif opt in ("-o", "--odir"):
            output_dir = arg
    print("Input directory is ", input_dir)
    print("Output file is ", output_dir)

    Compiler(input_dir, output_dir)


if __name__ == "__main__":
    main(sys.argv[1:])
