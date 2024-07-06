import os
import ffmpeg


class VideoCodec:
    """
    Handles the encoding and decoding of video files.

    :param video_path: Path to the input video file.
    :param output_folder: Directory to store decoded frames.
    :param frame_folder: Directory containing frames for encoding.
    :param threads: Number of threads to use for encoding/decoding. Default is 8.
    :param quality_scale: Quality scale for the output images (1-31). Default is 2.
    """

    def __init__(
        self,
        video_path: str,
        output_folder: str,
        frame_folder: str,
        threads: int = 8,
        quality_scale: int = 2,
    ):
        self.video_path = video_path
        self.output_folder = output_folder
        self.frame_folder = frame_folder
        self.threads = threads
        self.quality_scale = quality_scale

    def decode_video(self) -> None:
        """
        Extracts frames from a video file and stores them as images.

        :return: None
        """
        output_path = os.path.join(self.output_folder, "frame_%04d.jpeg")
        (
            ffmpeg.input(self.video_path)
            .output(output_path, vsync="0", qscale_v=self.quality_scale)
            .global_args("-threads", str(self.threads))
            .run()
        )

    def encode_video(self) -> None:
        """
        Compiles images back into a video file.

        :return: None
        """
        input_path = os.path.join(self.frame_folder, "frame_%04d.jpeg")
        (
            ffmpeg.input(input_path, framerate=30)
            .output(self.video_path, vcodec="libx264", pix_fmt="yuv420p")
            .global_args("-threads", str(self.threads))
            .run()
        )
