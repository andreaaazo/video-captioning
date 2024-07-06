import os
import ffmpeg


class VideoCodec:
    """
    VideoCodec handles the encoding and decoding of video files.

    :param [str] video_path: Path to the input video file.
    :param [str] output_folder: Directory to store decoded frames.
    :param [str] frame_folder: Directory containing frames for encoding.
    """

    def __init__(self, video_path, output_folder, frame_folder):
        self.video_path = video_path
        self.output_folder = output_folder
        self.frame_folder = frame_folder

    def decode_video(self):
        """
        decode_video extracts frames from a video file and stores them as images.

        :return: None
        """
        output_path = os.path.join(self.output_folder, "frame_%04d.jpeg")
        ffmpeg.input(self.video_path).output(output_path).run()

    def encode_video(self):
        """
        encode_video compiles images back into a video file.

        :return: None
        """
        input_path = os.path.join(self.frame_folder, "frame_%04d.jpeg")
        ffmpeg.input(input_path, framerate=30).output(self.video_path).run()
