import os
import ffmpeg
from src.utils.temp_file_manager import TempFileManager


class VideoCodec:
    """
    Handles the encoding and decoding of video files.

    :param video_path: [str] Path to the input video file.
    :param threads: [int] Number of threads to use for encoding/decoding. Default is 8.
    :param quality_scale: [int] Quality scale for the output images (1-31). Default is 2.
    """

    def __init__(
        self,
        video_path: str,
        temp_manager: TempFileManager,
        threads: int = 8,
        quality_scale: int = 2,
    ):
        """
        Initializes the VideoCodec with specified video path, threads, and quality scale.

        :param video_path: [str] Path to the input video file.
        :param threads: [int] Number of threads to use for encoding/decoding. Default is 8.
        :param quality_scale: [int] Quality scale for the output images (1-31). Default is 2.
        """
        self.video_path = video_path
        self.threads = threads
        self.quality_scale = quality_scale
        self.temp_manager = temp_manager
        self.temp_folder = self.temp_manager.create_temp_dir("video_temp_")
        self.frame_folder = os.path.join(self.temp_folder, "frames")
        self.audio_path = os.path.join(self.temp_folder, "audio.mp3")

        # Create the output and frame folders if they do not exist
        os.makedirs(self.frame_folder, exist_ok=True)
        os.makedirs(self.temp_folder, exist_ok=True)

    def decode_video(self) -> None:
        """
        Extracts frames from a video file and stores them as images.
        Also extracts audio from the video file.

        :return: None
        """
        output_path = os.path.join(self.frame_folder, "%d.jpeg")
        (
            ffmpeg.input(self.video_path)
            .output(
                output_path, vsync="0", q=self.quality_scale
            )  # Changed qscale_v to q
            .global_args("-threads", str(self.threads))
            .run()
        )

        # Extract audio
        (
            ffmpeg.input(self.video_path)
            .output(self.audio_path)
            .global_args("-threads", str(self.threads))
            .run()
        )

    def encode_video(self, framerate: int = 30) -> None:
        """
        Compiles images back into a video file with the original audio.

        :param framerate: [int] Framerate for the output video. Default is 30.
        :return: None
        """
        input_path = os.path.join(self.frame_folder, "%d.jpeg")
        temp_video_path = os.path.join(self.temp_folder, "temp_vid.mp4")

        # Encode video from frames
        (
            ffmpeg.input(input_path, framerate=framerate)
            .output(
                temp_video_path,
                vcodec="libx264",
                pix_fmt="yuv420p",
            )
            .global_args("-threads", str(self.threads))
            .run()
        )

        # Add audio to the video
        video = ffmpeg.input(temp_video_path)
        audio = ffmpeg.input(self.audio_path)

        (
            ffmpeg.concat(video, audio, v=1, a=1)
            .output(
                os.path.join(os.path.dirname(self.video_path), "final.mp4"),
                vcodec="libx264",
                acodec="aac",
            )
            .global_args("-threads", str(self.threads))
            .run()
        )

        # Clean up temporary video file
        os.remove(temp_video_path)

    def get_frame_folder(self) -> str:
        """
        Returns the path to the frame folder.

        :return: [str] Path to the frame folder.
        """
        return self.frame_folder
