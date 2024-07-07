import os
import ffmpeg
from typing import Optional, Dict, Any
from src.utils.temp_file_manager import TempFileManager


class VideoUtilities:
    """
    Provides various video processing utilities.

    :param video_path: [str] Path to the input video file.
    """

    def __init__(self, video_path: str, temp_manager: TempFileManager):
        """
        Initializes the VideoUtilities with the specified video path.

        :param video_path: [str] Path to the input video file.
        """
        self.video_path = video_path
        self.temp_manager = temp_manager

    def extract_audio(self) -> Optional[str]:
        """
        Extracts the audio from the video file and saves it in the 'temp' directory
        with the same base name but with an .mp3 extension.

        :return: [Optional[str]] Directory where the audio file is saved or None if an error occurs.
        """
        audio_path = self._get_audio_output_path()

        try:
            ffmpeg.input(self.video_path).output(audio_path).run()
            print(f"Audio extracted successfully: {audio_path}")
            return audio_path
        except ffmpeg.Error as e:
            print(f"Error occurred: {e.stderr.decode()}")
            return None

    def get_frame_count(self) -> Optional[int]:
        """
        Extracts the number of frames in the video file.

        :return: [Optional[int]] Number of frames in the video or None if an error occurs.
        """
        try:
            probe = ffmpeg.probe(self.video_path)
            video_stream = self._get_video_stream(probe)
            if video_stream and "nb_frames" in video_stream:
                return int(video_stream["nb_frames"])
            else:
                print("Could not determine the number of frames.")
                return None
        except (ffmpeg.Error, KeyError) as e:
            print(
                f"Error occurred: {e.stderr.decode() if isinstance(e, ffmpeg.Error) else str(e)}"
            )
            return None

    def get_frame_rate(self) -> Optional[float]:
        """
        Extracts the frame rate of the video file.

        :return: [Optional[float]] Frame rate of the video or None if an error occurs.
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
        except (ffmpeg.Error, KeyError) as e:
            print(
                f"Error occurred: {e.stderr.decode() if isinstance(e, ffmpeg.Error) else str(e)}"
            )
            return None

    def _get_audio_output_path(self) -> str:
        """
        Generates the output path for the extracted audio file in the 'temp' directory.

        :return: [str] Path to the output audio file.
        """
        temp_dir = self.temp_manager.create_temp_dir("audio_temp_")
        return os.path.join(
            temp_dir, f"{os.path.splitext(os.path.basename(self.video_path))[0]}.mp3"
        )

    def _get_video_stream(self, probe: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Retrieves the video stream information from the ffmpeg probe result.

        :param probe: [Dict[str, Any]] Probe result from ffmpeg.
        :return: [Optional[Dict[str, Any]]] Video stream information or None if not found.
        """
        return next(
            (
                stream
                for stream in probe.get("streams", [])
                if stream.get("codec_type") == "video"
            ),
            None,
        )
