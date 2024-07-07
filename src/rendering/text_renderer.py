import threading
import numpy as np
from freetype import Face
from src.cache.bitmap_cache import BitmapCache
from typing import Optional, Tuple
from concurrent.futures import ThreadPoolExecutor


class TextRenderer:
    """
    Handles rendering of text to an image using a specified font.

    :param font_path: [str] Path to the TrueType font file.
    :param char_size: [int] Character size in points.
    :param cache: [Optional[BitmapCache]] Instance for caching character bitmaps.
    """

    BLUE_CHANNEL = 0
    GREEN_CHANNEL = 1
    RED_CHANNEL = 2
    ALPHA_CHANNEL = 3

    TEXT_COLOR_RGB = (255, 255, 255)

    def __init__(
        self, font_path: str, char_size: int, cache: Optional[BitmapCache] = None
    ):
        """
        Initializes the TextRenderer with a specified font and character size.

        :param font_path: [str] Path to the TrueType font file.
        :param char_size: [int] Character size in points.
        :param cache: [Optional[BitmapCache]] Instance for caching character bitmaps.
        """
        self.face = Face(font_path)
        self.char_size = char_size * 64  # FreeType uses 1/64th points
        self.face.set_char_size(self.char_size)
        self.slot = self.face.glyph
        self.cache = cache
        self.lock = threading.Lock()  # Lock for thread-safe cache access
        self.kerning_cache = {}  # Cache for kerning values

    def calculate_text_size(self, text: str) -> Tuple[int, int, int]:
        """
        Calculate dimensions of the image needed to render the text.

        :param text: [str] Text to render.
        :return: [Tuple[int, int, int]] (width, height, baseline) of the image.
        """
        width, height, baseline = 0, 0, 0
        previous_char = 0

        for char in text:
            self.face.load_char(char)
            bitmap = self.slot.bitmap
            height = max(height, bitmap.rows - self.slot.bitmap_top)
            baseline = max(baseline, -self.slot.bitmap_top)
            kerning = self.get_kerning(previous_char, char)
            width += (self.slot.advance.x >> 6) + (kerning.x >> 6)
            previous_char = char

        return width, height, baseline

    def get_kerning(self, previous_char: int, current_char: int) -> Tuple[int, int]:
        """
        Get the kerning value between two characters, using a cache to store results.

        :param previous_char: [int] The previous character code.
        :param current_char: [int] The current character code.
        :return: [Tuple[int, int]] The kerning values.
        """
        key = (previous_char, current_char)
        if key not in self.kerning_cache:
            self.kerning_cache[key] = self.face.get_kerning(previous_char, current_char)
        return self.kerning_cache[key]

    def render_text(self, text: str, image: np.ndarray) -> np.ndarray:
        """
        Render the text into an image.

        :param text: [str] Text to render.
        :param image: [np.ndarray] Background image to render the text on.
        :return: [np.ndarray] Numpy array representing the rendered image.
        """
        self.preload_cache(text)  # Preload cache to optimize rendering

        text_width, text_height, baseline = self.calculate_text_size(text)
        image_height, image_width, _ = image.shape

        # Calculate starting positions to center the text
        x_position = (image_width - text_width) // 2
        y_position = (image_height - text_height) // 2 + baseline

        previous_char = 0
        tasks = []

        with ThreadPoolExecutor() as executor:
            for char in text:
                cache_key = (char, self.char_size)
                if self.cache and cache_key in self.cache.cache:
                    with self.lock:
                        bitmap_3d, left, top = self.cache.cache[cache_key]
                else:
                    self.face.load_char(char)
                    bitmap = self.slot.bitmap
                    top = self.slot.bitmap_top
                    left = self.slot.bitmap_left
                    bitmap_2d = np.array(bitmap.buffer, dtype=np.uint8).reshape(
                        bitmap.rows, bitmap.width
                    )
                    bitmap_3d = self.get_bitmap_3d(bitmap_2d)
                    if self.cache:
                        with self.lock:
                            self.cache.cache[cache_key] = (bitmap_3d, left, top)

                y_char_position = y_position - top
                kerning = self.get_kerning(previous_char, char)
                x_position += kerning.x >> 6

                tasks.append(
                    executor.submit(
                        self.apply_bitmap_to_image,
                        image,
                        bitmap_3d,
                        x_position + left,
                        y_char_position,
                    )
                )

                x_position += self.slot.advance.x >> 6
                previous_char = char

            for task in tasks:
                task.result()

        if self.cache:
            self.cache.save_cache()
        return image

    def get_bitmap_3d(self, bitmap_2d: np.ndarray) -> np.ndarray:
        """
        Obtain a 3D bitmap by rendering the text to an RGBA image.

        :param bitmap_2d: [np.ndarray] 2D bitmap buffer for the rendered image.
        :return: [np.ndarray] Rendered 3D bitmap buffer.
        """
        bitmap_3d = np.zeros((*bitmap_2d.shape, 4), dtype=np.uint8)
        bitmap_3d[:, :, self.RED_CHANNEL] = self.TEXT_COLOR_RGB[0]
        bitmap_3d[:, :, self.GREEN_CHANNEL] = self.TEXT_COLOR_RGB[1]
        bitmap_3d[:, :, self.BLUE_CHANNEL] = self.TEXT_COLOR_RGB[2]
        bitmap_3d[:, :, self.ALPHA_CHANNEL] = bitmap_2d
        return bitmap_3d

    def apply_bitmap_to_image(
        self, image: np.ndarray, bitmap: np.ndarray, x: int, y: int
    ):
        """
        Apply a bitmap onto an image at the specified position using alpha blending.

        :param image: [np.ndarray] Background image.
        :param bitmap: [np.ndarray] 3D numpy array of the bitmap to render.
        :param x: [int] X-coordinate on the image to place the bitmap.
        :param y: [int] Y-coordinate on the image to place the bitmap.
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

    @staticmethod
    def pixel_alpha_blending(bg_pixel: np.ndarray, fg_pixel: np.ndarray) -> np.ndarray:
        """
        Perform alpha blending operation on the background and foreground pixel.

        :param bg_pixel: [np.ndarray] Pixel values of the background image.
        :param fg_pixel: [np.ndarray] Pixel values of the foreground image.
        :return: [np.ndarray] Final pixel value after alpha blending.
        """
        alpha = fg_pixel[TextRenderer.ALPHA_CHANNEL] / 255.0
        blended_pixel = (1 - alpha) * bg_pixel[:3] + alpha * fg_pixel[:3]
        return np.uint8(np.append(blended_pixel, 255))

    def preload_cache(self, text: str):
        """
        Preload characters into the cache if the text is known in advance.

        :param text: [str] Text to render.
        """
        with self.lock:  # Use a single lock to preload cache
            for char in text:
                cache_key = (char, self.char_size)
                if self.cache and cache_key not in self.cache.cache:
                    self.face.load_char(char)
                    bitmap = self.slot.bitmap
                    top = self.slot.bitmap_top
                    left = self.slot.bitmap_left
                    bitmap_2d = np.array(bitmap.buffer, dtype=np.uint8).reshape(
                        bitmap.rows, bitmap.width
                    )
                    bitmap_3d = self.get_bitmap_3d(bitmap_2d)
                    self.cache.cache[cache_key] = (bitmap_3d, left, top)
