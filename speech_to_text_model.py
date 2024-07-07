from faster_whisper import WhisperModel
from typing import Tuple, Any


class SpeechToTextModel:
    """
    Service for handling speech-to-text transcription using a specified model.

    :param model_name: [str] Name of the model to use for transcription.
    """

    def __init__(self, model_name: str = "medium"):
        """
        Initializes the SpeechToTextModel with a specified model.

        :param model_name: [str] Name of the model to use for transcription.
        """
        self.model = WhisperModel(model_name)

    def transcribe_audio(self, audio_path: str) -> Tuple[Any, Any]:
        """
        Transcribes the given audio file and returns the segments and information.

        :param audio_path: [str] Path to the audio file.
        :return: [tuple] Segments and info from the transcription.
        """
        return self.model.transcribe(audio_path, word_timestamps=True)
