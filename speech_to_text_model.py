from faster_whisper import WhisperModel


class SpeechToTextModel:
    """
    Handles the transcription model for converting speech to text.

    :param model_name: Name of the model to use for transcription.
    """

    def __init__(self, model_name: str = "medium"):
        self.model = WhisperModel(model_name)

    def transcribe(self, audio_path: str):
        """
        Transcribes the audio file and returns segments and info.

        :param audio_path: Path to the audio file.
        :return: Segments and info from the transcription.
        """
        return self.model.transcribe(audio_path, word_timestamps=True)
