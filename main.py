import os
from text_renderer import TextRenderer
from utils import read_image, write_image
from bitmap_cache import BitmapCache
from video_codec import VideoCodec
from video_utilities import VideoUtilities
import time
from speech_to_text import SpeechToText, SpeechToTextModel
from audio_file import AudioFile
from temp_file_manager import TempFileManager

BASE_PATH = os.path.dirname(__file__)


def render_text_on_image():
    """
    Function to render text on a image
    """
    start_time = time.time()  # Record the start time

    font_path = "font.ttf"
    char_size = 800
    text = "RENDER TEST"

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


def speech_to_text():
    model = SpeechToTextModel("medium")
    audio_file = AudioFile(os.path.join(BASE_PATH, "audio.wav"))
    speech_to_text = SpeechToText(model)
    print(speech_to_text.word_level_timestamps(audio_file))


def main():
    font_path = "font.ttf"
    char_size = 100
    cache = BitmapCache()
    temp_manager = TempFileManager()

    video_utils = VideoUtilities("example.mp4", temp_manager)
    audio = video_utils.extract_audio()
    model = SpeechToTextModel()
    audio = AudioFile(audio)

    word_level_text = SpeechToText(model).word_level_timestamps(audio)
    framerate = video_utils.get_frame_rate()
    frames = video_utils.get_frame_count()

    renderer = TextRenderer(font_path, char_size)
    video_codec = VideoCodec("example.mp4", temp_manager)
    video_codec.decode_video()

    frame_path = video_codec.get_frame_folder()

    for au_beg, au_end, word in word_level_text:
        begin_frame = int(au_beg * framerate)
        end_frame = int(au_end * framerate)
        if begin_frame == 0:
            begin_frame = 1
        if frames > end_frame:
            for frame_num in range(begin_frame, end_frame):
                frame_rendered = renderer.render_text(
                    word,
                    read_image(os.path.join(frame_path, str(frame_num) + ".jpeg")),
                )
                print(frame_num)
                write_image(
                    frame_rendered, os.path.join(frame_path, str(frame_num) + ".jpeg")
                )
        else:
            break

    video_codec.encode_video(framerate)

    temp_manager.clean_up()


if __name__ == "__main__":
    main()
