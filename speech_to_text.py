from faster_whisper import WhisperModel
from audio_file import AudioFile
from speech_to_text_model import SpeechToTextModel


class SpeechToText:
    """
    Converts speech in an audio file to text with word-level timestamps.

    :param model: Instance of SpeechToTextModel for transcription.
    """

    def __init__(self, model: SpeechToTextModel):
        self.model = model

    def word_level_timestamps(self, audio_file: AudioFile) -> list:
        """
        Transcribes the audio file and returns word-level timestamps.

        :param audio_file: An instance of AudioFile containing the path to the audio.
        :return: A list of word-level timestamps. Each entry contains [start, end, word].
        """
        segments, _ = self.model.transcribe(audio_file.get_path())

        words = []
        for segment in segments:
            words.extend([(word.start, word.end, word.word) for word in segment.words])

        return words
