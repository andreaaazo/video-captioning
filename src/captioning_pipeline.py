import os
from typing import List, Tuple

from src.cache.bitmap_cache import BitmapCache
from src.utils.temp_file_manager import TempFileManager
from src.video.video_utilities import VideoUtilities
from src.audio.speech_to_text import SpeechToText, SpeechToTextModel
from src.rendering.text_renderer import TextRenderer
from src.video.video_codec import VideoCodec
from src.rendering.image_utils import ImageUtils
from src.audio.audio_file import AudioFile


class CaptioningPipeline:
    """
    CaptioningPipeline manages the entire process of generating captions for a video.

    :param video_path: Path to the input video file.
    :param font_path: Path to the font file used for rendering text.
    :param char_size: Size of the characters in the rendered text.
    """

    def __init__(self, video_path: str, font_path: str, char_size: int):
        self.font_path = font_path
        self.char_size = char_size
        self.video_path = video_path

        self.cache = BitmapCache()
        self.temp_manager = TempFileManager()
        self.video_utils = VideoUtilities(video_path, self.temp_manager)
        self.model = SpeechToTextModel()
        self.renderer = TextRenderer(font_path, char_size)
        self.video_codec = VideoCodec(video_path, self.temp_manager)

    def extract_audio(self) -> AudioFile:
        """
        Extracts audio from the video file.

        :return: AudioFile object containing the path to the extracted audio.
        """
        audio_path = self.video_utils.extract_audio()
        return AudioFile(audio_path)

    def get_word_level_text(self, audio: AudioFile) -> List[Tuple[float, float, str]]:
        """
        Converts audio to word-level timestamps using Speech-to-Text.

        :param audio: AudioFile object containing the audio data.
        :return: List of tuples containing word-level timestamps and text.
        """
        stt = SpeechToText(self.model)
        return stt.word_level_timestamps(audio)

    def render_captions(
        self,
        word_level_text: List[Tuple[float, float, str]],
        framerate: float,
        frames: int,
    ):
        """
        Renders captions on video frames based on word-level timestamps.

        :param word_level_text: List of tuples containing word-level timestamps and text.
        :param framerate: Frame rate of the video.
        :param frames: Total number of frames in the video.
        """
        frame_path = self.video_codec.get_frame_folder()
        for au_beg, au_end, word in word_level_text:
            begin_frame = max(1, int(au_beg * framerate))
            end_frame = int(au_end * framerate)
            if frames > end_frame:
                for frame_num in range(begin_frame, end_frame):
                    frame_rendered = self.renderer.render_text(
                        word,
                        ImageUtils.read_image(
                            os.path.join(frame_path, f"{frame_num}.jpeg")
                        ),
                    )
                    ImageUtils.write_image(
                        frame_rendered, os.path.join(frame_path, f"{frame_num}.jpeg")
                    )
            else:
                break

    def run(self):
        """
        Executes the captioning pipeline: extracts audio, generates word-level text,
        decodes video, renders captions, encodes video, and cleans up temporary files.
        """
        audio = self.extract_audio()
        word_level_text = self.get_word_level_text(audio)
        framerate = self.video_utils.get_frame_rate()
        frames = self.video_utils.get_frame_count()

        self.video_codec.decode_video()
        self.render_captions(word_level_text, framerate, frames)
        self.video_codec.encode_video(framerate)
        self.temp_manager.clean_up()
