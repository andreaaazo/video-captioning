import cv2 as cv
import numpy as np
from freetype import Face


class TextToImage:
    """
    TextToImage handles the rendering of text to an image using a specified font.

    :param font_path: Path to the TrueType font file.
    :param char_size: Character size in points.
    """

    def __init__(self, font_path: str, char_size: int):
        self.face = Face(font_path)
        self.face.set_char_size(char_size * 64)
        self.slot = self.face.glyph

    def calculate_image_size(self, text: str) -> tuple:
        """
        Calculate the dimensions of the image needed to render the text.

        :param text: Text to render.
        :return: Tuple containing [width], [height], and [baseline] of the image.
        """
        width, height, baseline = 0, 0, 0
        previous = 0
        for letter in text:
            self.face.load_char(letter)
            bitmap = self.slot.bitmap
            height = max(
                height, bitmap.rows + max(0, -(self.slot.bitmap_top - bitmap.rows))
            )
            baseline = max(baseline, max(0, -(self.slot.bitmap_top - bitmap.rows)))
            kerning = self.face.get_kerning(previous, letter)
            width += self.slot.advance.x >> 6 + kerning.x >> 6
            previous = letter
        return width, height, baseline

    def render_text(self, text: str) -> np.ndarray:
        """
        Render the text into an image.

        :param text: Text to render.
        :return: Numpy array representing the rendered image.
        """
        width, height, baseline = self.calculate_image_size(text)
        image = np.zeros((height, width), dtype=np.ubyte)

        x, y = 0, 0
        previous = 0
        for letter in text:
            self.face.load_char(letter)
            top = self.slot.bitmap_top
            left = self.slot.bitmap_left
            w, h = self.slot.bitmap.width, self.slot.bitmap.rows
            y = height - baseline - top
            kerning = self.face.get_kerning(previous, letter)
            x += kerning.x >> 6
            image[y : y + h, x + left : x + left + w] += np.array(
                self.slot.bitmap.buffer, dtype="ubyte"
            ).reshape(h, w)
            x += self.slot.advance.x >> 6
            previous = letter

        return image


def main():
    """
    Main function to execute the text rendering and save the output image.
    """
    text_to_image = TextToImage("font.ttf", 48)
    text = "Elena stai bene?"
    image = text_to_image.render_text(text)
    cv.imwrite("result.jpg", image)


if __name__ == "__main__":
    main()
