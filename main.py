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
        for i, c in enumerate(text):
            self.face.load_char(c)
            bitmap = self.slot.bitmap
            height = max(
                height, bitmap.rows + max(0, -(self.slot.bitmap_top - bitmap.rows))
            )
            baseline = max(baseline, max(0, -(self.slot.bitmap_top - bitmap.rows)))
            kerning = self.face.get_kerning(previous, c)
            width += (self.slot.advance.x >> 6) + (kerning.x >> 6)
            previous = c
        return width, height, baseline

    def render_text(self, text: str) -> np.ndarray:
        """
        Render the text into an image.

        :param text: Text to render.
        :return: Numpy array representing the rendered image.
        """
        width, height, baseline = self.calculate_image_size(text)

        image = np.zeros((height, width, 3), dtype=np.ubyte)

        x, y = 0, 0
        previous = 0
        for c in text:
            self.face.load_char(c)
            bitmap = self.slot.bitmap
            top = self.slot.bitmap_top
            left = self.slot.bitmap_left
            w, h = bitmap.width, bitmap.rows
            y = height - baseline - top
            kerning = self.face.get_kerning(previous, c)
            x += kerning.x >> 6

            bitmap_2d = np.array(bitmap.buffer, dtype="ubyte").reshape(h, w)

            bitmap_3d = np.zeros((h, w, 3), dtype="ubyte")
            bitmap_3d[:, :, 0] = bitmap_2d  # Canale rosso
            bitmap_3d[:, :, 1] = bitmap_2d  # Canale verde
            bitmap_3d[:, :, 2] = bitmap_2d  # Canale blu

            image[y : y + h, x + left : x + left + w] += bitmap_3d
            x += self.slot.advance.x >> 6
            previous = c

        return image


def main():
    """
    Main function to execute the text rendering and save the output image.
    """
    text_to_image = TextToImage("font.ttf", 48)
    text = "Elena stai beneeasdfasdfasdfasdfs?"
    image = text_to_image.render_text(text)
    cv.imwrite("result.jpg", image)


if __name__ == "__main__":
    main()
