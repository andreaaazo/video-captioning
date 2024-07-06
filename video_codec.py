import os
import ffmpeg


class VideoCodec:
    """
    VideoCodec handles the encoding and decoding of video files.

    :param [str] video_path: Path to the input video file.
    :param [str] output_folder: Directory to store decoded frames.
    :param [str] frame_folder: Directory containing frames for encoding.
    :param [int] threads: 1 min. Number of threads to use for encoding/decoding.
    :param [int] quality_scale: 1-31 Quality scale for the output images.
    """

    def __init__(
        self, video_path, output_folder, frame_folder, threads=8, quality_scale=2
    ):
        self.video_path = video_path
        self.output_folder = output_folder
        self.frame_folder = frame_folder
        self.threads = threads
        self.quality_scale = quality_scale

    def decode_video(self):
        """
        decode_video extracts frames from a video file and stores them as images.

        :return: None
        """
        output_path = os.path.join(self.output_folder, "frame_%04d.jpeg")
        (
            ffmpeg.input(self.video_path)
            .output(output_path, vsync="0", qscale_v=self.quality_scale)
            .global_args("-threads", str(self.threads))
            .run()
        )

    def encode_video(self):
        """
        encode_video compiles images back into a video file.

        :return: None
        """
        input_path = os.path.join(self.frame_folder, "frame_%04d.jpeg")
        (
            ffmpeg.input(input_path, framerate=30)
            .output(self.video_path, vcodec="libx264", pix_fmt="yuv420p")
            .global_args("-threads", str(self.threads))
            .run()
        )
