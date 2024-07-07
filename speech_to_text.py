from typing import List, Tuple
from audio_file import AudioFile
from speech_to_text_model import SpeechToTextModel


class SpeechToText:
    """
    Converts speech in an audio file to text with word-level timestamps.

    :param model: [SpeechToTextModel] Instance of SpeechToTextModel for transcription.
    """

    def __init__(self, model: SpeechToTextModel):
        """
        Initializes the SpeechToText with a specified model.

        :param model: [SpeechToTextModel] Instance of SpeechToTextModel for transcription.
        """
        self.model = model

    def word_level_timestamps(
        self, audio_file: AudioFile
    ) -> List[Tuple[float, float, str]]:
        """
        Transcribes the audio file and returns word-level timestamps.

        :param audio_file: [AudioFile] An instance of AudioFile containing the path to the audio.
        :return: [List[Tuple[float, float, str]]] A list of word-level timestamps. Each entry contains [start, end, word].
        """
        segments, _ = self.model.transcribe_audio(audio_file.get_path())

        # Collect word-level timestamps
        words = [
            (word.start, word.end, word.word)
            for segment in segments
            for word in segment.words
        ]

        return words
