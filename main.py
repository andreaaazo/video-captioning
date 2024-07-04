from freetype import Face
import numpy as np
import cv2 as cv


def main():
    word = "Elena stai bene?"

    face = Face("font.ttf")
    face.set_char_size(48 * 64)
    slot = face.glyph

    width, height, baseline = 0, 0, 0
    previous = 0
    for letter in word:
        face.load_char(letter)
        bitmap = slot.bitmap
        height = max(height, bitmap.rows + max(0, -(slot.bitmap_top - bitmap.rows)))
        baseline = max(baseline, max(0, -(slot.bitmap_top - bitmap.rows)))
        kerning = face.get_kerning(previous, letter)
        width += slot.advance.x >> 6 + (kerning.x >> 6)
        previous = letter

    test_image = np.zeros((height, width), dtype=np.ubyte)

    x, y = 0, 0
    previous = 0
    for letter in word:
        face.load_char(letter)
        top = slot.bitmap_top
        left = slot.bitmap_left
        w, h = bitmap.width, bitmap.rows
        y = height - baseline - top
        kerning = face.get_kerning(previous, letter)
        x += kerning.x >> 6
        test_image[y : y + h, x + left : x + left + w] += np.array(
            bitmap.buffer, dtype="ubyte"
        ).reshape(h, w)
        x += slot.advance.x >> 6
        previous = letter

    return test_image


if __name__ == "__main__":
    cv.imwrite("result.jpg", main())
