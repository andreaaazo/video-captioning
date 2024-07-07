class AudioFile:
    """
    Represents an audio file with a specified path.

    :param audio_path: [str] Path to the audio file.
    """

    def __init__(self, audio_path: str):
        """
        Initializes the AudioFile with the specified audio path.

        :param audio_path: [str] Path to the audio file.
        """
        self.audio_path = audio_path

    def get_path(self) -> str:
        """
        Returns the path of the audio file.

        :return: [str] Path to the audio file.
        """
        return self.audio_path
