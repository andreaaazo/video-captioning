import ffmpeg
import os


class VideoUtilities:
    """
    VideoUtilities provides various video processing utilities.

    :param video_path: Path to the input video file [str].
    """

    def __init__(self, video_path):
        self.video_path = video_path

    def extract_audio(self):
        """
        Extracts the audio from the video file and saves it in the 'temp' directory
        with the same base name but with an .mp3 extension.

        :return: The directory where the audio file is saved [str].
        """
        audio_path = self._get_audio_output_path()

        try:
            ffmpeg.input(self.video_path).output(audio_path).run()
            print(f"Audio extracted successfully: {audio_path}")
            return audio_path
        except ffmpeg.Error as e:
            print(f"Error occurred: {e.stderr.decode()}")
            return None

    def get_frame_count(self):
        """
        Extracts the number of frames in the video file.

        :return: The number of frames in the video [int] or None if an error occurs.
        """
        try:
            probe = ffmpeg.probe(self.video_path)
            video_stream = self._get_video_stream(probe)
            if video_stream and "nb_frames" in video_stream:
                return int(video_stream["nb_frames"])
            else:
                print("Could not determine the number of frames.")
                return None
        except ffmpeg.Error as e:
            print(f"Error occurred: {e.stderr.decode()}")
            return None
        except KeyError:
            print("Could not find video stream information.")
            return None

    def get_frame_rate(self):
        """
        Extracts the frame rate of the video file.

        :return: The frame rate of the video [float] or None if an error occurs.
        """
        try:
            probe = ffmpeg.probe(self.video_path)
            video_stream = self._get_video_stream(probe)
            if video_stream and "r_frame_rate" in video_stream:
                num, denom = map(int, video_stream["r_frame_rate"].split("/"))
                return num / denom
            else:
                print("Could not determine the frame rate.")
                return None
        except ffmpeg.Error as e:
            print(f"Error occurred: {e.stderr.decode()}")
            return None
        except KeyError:
            print("Could not find video stream information.")
            return None

    def _get_audio_output_path(self):
        """
        Generates the output path for the extracted audio file in the 'temp' directory.

        :return: Path to the output audio file [str].
        """
        temp_dir = os.path.join(os.path.dirname(self.video_path), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        return os.path.join(temp_dir, f"audio.mp3")

    def _get_video_stream(self, probe):
        """
        Retrieves the video stream information from the ffmpeg probe result.

        :param probe: The probe result from ffmpeg [dict].
        :return: The video stream information [dict] or None if not found.
        """
        return next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
            None,
        )
