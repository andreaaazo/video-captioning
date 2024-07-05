import cv2 as cv
import numpy as np
from freetype import Face
import os


class TextRenderer:
    """
    TextRenderer handles rendering of text to an image using a specified font.

    :param font_path: Path to the TrueType font file.
    :param char_size: Character size in points.
    """

    RED_CHANNEL = 0
    GREEN_CHANNEL = 1
    BLUE_CHANNEL = 2
    ALPHA_CHANNEL = 3

    def __init__(self, font_path: str, char_size: int):
        # Initialize font face
        self.face = Face(font_path)
        self.face.set_char_size(char_size * 64)
        self.slot = self.face.glyph

    def calculate_text_size(self, text: str) -> tuple:
        """
        Calculate dimensions of the image needed to render the text.

        :param text: Text to render.
        :return: (width, height, baseline) of the image.
        """
        width, height, baseline = 0, 0, 0
        previous_char = 0

        for char in text:
            self.face.load_char(char)
            bitmap = self.slot.bitmap
            height = max(height, bitmap.rows - self.slot.bitmap_top)
            baseline = max(baseline, -self.slot.bitmap_top)
            kerning = self.face.get_kerning(previous_char, char)
            width += (self.slot.advance.x >> 6) + (kerning.x >> 6)
            previous_char = char

        return width, height, baseline

    def render_text(self, text: str, image: np.ndarray) -> np.ndarray:
        """
        Render the text into an image.

        :param text: Text to render.
        :param image: Background image to render the text on.
        :return: Numpy array representing the rendered image.
        """
        width, height, baseline = self.calculate_text_size(text)
        x_position = 0
        previous_char = 0

        for char in text:
            self.face.load_char(char)
            bitmap = self.slot.bitmap
            top = self.slot.bitmap_top
            left = self.slot.bitmap_left
            y_position = height - baseline - top
            kerning = self.face.get_kerning(previous_char, char)
            x_position += kerning.x >> 6

            bitmap_2d = np.array(bitmap.buffer, dtype=np.uint8).reshape(
                bitmap.rows, bitmap.width
            )
            bitmap_3d = self.get_bitmap_3d(bitmap_2d)

            self.apply_bitmap_to_image(image, bitmap_3d, x_position + left, y_position)

            x_position += self.slot.advance.x >> 6
            previous_char = char

        return image

    def get_bitmap_3d(self, bitmap_2d: np.ndarray) -> np.ndarray:
        """
        Obtain a 3D bitmap by rendering the text to an RGBA image.

        :param bitmap_2d: 2D bitmap buffer for the rendered image.
        :return: Rendered 3D bitmap buffer.
        """
        bitmap_3d = np.zeros((*bitmap_2d.shape, 4), dtype=np.uint8)
        bitmap_3d[:, :, self.RED_CHANNEL] = 255
        bitmap_3d[:, :, self.GREEN_CHANNEL] = 255
        bitmap_3d[:, :, self.BLUE_CHANNEL] = 255
        bitmap_3d[:, :, self.ALPHA_CHANNEL] = bitmap_2d
        return bitmap_3d

    def apply_bitmap_to_image(
        self, image: np.ndarray, bitmap: np.ndarray, x: int, y: int
    ):
        """
        Apply a bitmap onto an image at the specified position using alpha blending.

        :param image: Background image.
        :param bitmap: 3D numpy array of the bitmap to render.
        :param x: X-coordinate on the image to place the bitmap.
        :param y: Y-coordinate on the image to place the bitmap.
        """
        h, w, _ = bitmap.shape
        image_h, image_w, _ = image.shape

        x0, x1 = max(x, 0), min(x + w, image_w)
        y0, y1 = max(y, 0), min(y + h, image_h)

        img_slice = image[y0:y1, x0:x1]
        bitmap_slice = bitmap[y0 - y : y1 - y, x0 - x : x1 - x]

        alpha = bitmap_slice[:, :, self.ALPHA_CHANNEL, np.newaxis] / 255.0
        blended_slice = (1 - alpha) * img_slice[:, :, :3] + alpha * bitmap_slice[
            :, :, :3
        ]
        image[y0:y1, x0:x1] = np.concatenate(
            (np.uint8(blended_slice), img_slice[:, :, 3, np.newaxis]), axis=2
        )

    def pixel_alpha_blending(
        self, bg_pixel: np.ndarray, fg_pixel: np.ndarray
    ) -> np.ndarray:
        """
        Perform alpha blending operation on the background and foreground pixel.

        :param bg_pixel: Pixel values of the background image.
        :param fg_pixel: Pixel values of the foreground image.
        :return: Final pixel value after alpha blending.
        """
        alpha = fg_pixel[self.ALPHA_CHANNEL] / 255.0
        blended_pixel = (1 - alpha) * bg_pixel[:3] + alpha * fg_pixel[:3]
        return np.uint8(np.append(blended_pixel, 255))


def read_image(img_path: str) -> np.ndarray:
    """
    Read and convert an image to BGRA format.

    :param img_path: Path to the image file.
    :return: BGRA formatted image.
    """
    img = cv.imread(img_path, cv.IMREAD_UNCHANGED)
    return cv.cvtColor(img, cv.COLOR_BGR2BGRA)


def write_image(img: np.ndarray, output_path: str):
    """
    Save the rendered image to a file.

    :param img: Image to save.
    :param output_path: Path to save the image.
    """
    cv.imwrite(output_path, img)


def main():
    """
    Main function to execute the text rendering and save the output image.
    """
    font_path = "font.ttf"
    char_size = 180
    text = "Sample text for rendering."
    img_path = os.path.join(os.path.dirname(__file__), "example.jpg")

    renderer = TextRenderer(font_path, char_size)
    img = read_image(img_path)
    rendered_image = renderer.render_text(text, img)
    write_image(rendered_image, "result.jpg")


if __name__ == "__main__":
    main()
