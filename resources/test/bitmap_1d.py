from os.path import splitext
from PIL import Image, ImageOps


def main():
    src = Image.open(splitext(__file__)[0] + ".png").convert("1")
    w, h = src.size
    dst = bytearray()
    for x in range(w):
        column = 0
        for y in range(h):
            if src.getpixel((x, y)):
                column |= (1 << y)
        dst.append(column)
    print(bytes(dst))

    good = src
    bad1 = ImageOps.flip(good)
    bad2 = ImageOps.mirror(good)
    bad3 = ImageOps.mirror(bad1)

    for x in range(w):
        for y in range(h):
            xy = x, y
            goodval = good.getpixel(xy)
            if bad1.getpixel(xy) == goodval:
                continue
            if bad2.getpixel(xy) == goodval:
                continue
            if bad3.getpixel(xy) == goodval:
                continue
            print(xy, "should be", goodval)

    dst = Image.new("RGB", (w * 2 + 1, h * 2 + 1), (255, 0, 158))
    dst.paste(good, (0, 0))
    dst.paste(bad1, (0, h + 1))
    dst.paste(bad2, (w + 1, 0))
    dst.paste(bad3, (w + 1, h + 1))
    dst.save("check.png")


if __name__ == "__main__":
    main()
