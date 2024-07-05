import cv2 as cv
import numpy as np
from freetype import Face
import os


class TextToImage:
    """
    TextToImage handles the rendering of text to an image using a specified font.

    :param font_path: Path to the TrueType font file.
    :param char_size: Character size in points.
    """

    def __init__(self, font_path: str, char_size: int):
        """
        Initialize TextToImage with the font and character size.

        :param font_path: Path to the TrueType font file.
        :param char_size: Character size in points.
        """
        self.face = Face(font_path)
        self.face.set_char_size(char_size * 64)
        self.slot = self.face.glyph

    def calculate_text_size(self, text: str) -> tuple:
        """
        Calculate the dimensions of the image needed to render the text.

        :param text: Text to render.
        :return: Tuple containing width, height, and baseline of the image.
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

    def render_text(self, text: str, image) -> np.ndarray:
        """
        Render the text into an image.

        :param text: Text to render.
        :return: Numpy array representing the rendered image.
        """
        width, height, baseline = self.calculate_text_size(text)

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

            bitmap_2d = np.array(bitmap.buffer, dtype=np.uint8).reshape(h, w)
            bitmap_3d = np.zeros((h, w, 4), dtype="ubyte")
            bitmap_3d[:, :, 0] = 255  # Canale rosso
            bitmap_3d[:, :, 1] = 255  # Canale verde
            bitmap_3d[:, :, 2] = 255  # Canale blu
            bitmap_3d[:, :, 3] = bitmap_2d

            for i in range(h):
                for j in range(w):
                    image[y + i, x + left + j] = self.pixel_alpha_blending(
                        image[y + i, x + left + j], bitmap_3d[i, j]
                    )
            x += self.slot.advance.x >> 6
            previous = c

        return image

    def pixel_alpha_blending(self, bg_pixel, foreground_pixel):
        r_bg = bg_pixel[0]
        r_fg = foreground_pixel[0]

        g_bg = bg_pixel[1]
        g_fg = foreground_pixel[1]

        b_bg = bg_pixel[2]
        b_fg = foreground_pixel[2]

        a_fg = foreground_pixel[3] / 255

        R = (r_fg * a_fg) + (r_bg * (1.0 - a_fg))
        G = (g_fg * a_fg) + (g_bg * (1.0 - a_fg))
        B = (b_fg * a_fg) + (b_bg * (1.0 - a_fg))

        return np.uint8([int(R), int(G), int(B), 255])


def main():
    """
    Main function to execute the text rendering and save the output image.
    """
    text_to_image = TextToImage("font.ttf", 180)
    text = "Elena stai beneeasdfasdfasdfasdfs?"

    IMG_PATH = os.path.join(os.path.dirname(__file__), "example.jpg")
    IMG = cv.imread(IMG_PATH, cv.IMREAD_UNCHANGED)
    IMG = cv.cvtColor(IMG, cv.COLOR_BGR2BGRA)
    image = text_to_image.render_text(text, IMG)
    cv.imwrite("result.png", image)


if __name__ == "__main__":
    main()
