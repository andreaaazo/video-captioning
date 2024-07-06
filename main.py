import os
from text_renderer import TextRenderer
from utils import read_image, write_image
from bitmap_cache import BitmapCache
from video_codec import VideoCodec
import time


def main():
    """
    Main function to execute the text rendering and save the output image.
    """
    start_time = time.time()  # Record the start time

    font_path = "font.ttf"
    char_size = 400
    text = "NATURE"

    BASE_PATH = os.path.dirname(__file__)

    cache = BitmapCache()
    renderer = TextRenderer(
        font_path,
        char_size,
        cache,
    )
    renderer.TEXT_COLOR_RGB = (247, 231, 220)

    img = read_image(os.path.join(BASE_PATH, "example.jpg"))

    rendered_image = renderer.render_text(text, img)
    write_image(rendered_image, os.path.join(BASE_PATH, "result.jpg"))

    end_time = time.time()  # Record the end time
    execution_time = end_time - start_time  # Calculate the execution time
    print(f"Execution time of : {execution_time:.6f} seconds")


if __name__ == "__main__":
    main()
