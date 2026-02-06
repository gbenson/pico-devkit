from os.path import splitext
from PIL import Image


def main():
    src = Image.open(splitext(__file__)[0] + ".png")
    src = src.crop((16, 0, 23, src.height))
    src = src.transpose(method=Image.Transpose.ROTATE_90)
    src = src.convert("1")
    src.save("check.png")

    w, h = src.size
    dst = bytearray()
    for x in range(w):
        column = 0
        for y in range(h):
            if src.getpixel((x, y)):
                column |= (1 << y)
        dst.append(column)
    print(bytes(dst))


if __name__ == "__main__":
    main()
