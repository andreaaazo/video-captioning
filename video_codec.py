import os
import ffmpeg


class VideoCodec:
    """
    Handles the encoding and decoding of video files.

    :param video_path: Path to the input video file.
    :param threads: Number of threads to use for encoding/decoding. Default is 8.
    :param quality_scale: Quality scale for the output images (1-31). Default is 2.
    """

    def __init__(self, video_path: str, threads: int = 8, quality_scale: int = 2):
        self.video_path = video_path
        self.threads = threads
        self.quality_scale = quality_scale
        self.temp_folder = os.path.join(os.path.dirname(video_path), "temp")
        self.frame_folder = os.path.join(os.path.dirname(video_path), "temp", "frames")
        self.audio_path = os.path.join(os.path.dirname(video_path), "temp", "audio.mp3")

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

    def encode_video(self, framerate: int = 30) -> None:
        """
        Compiles images back into a video file with the original audio.

        :param framerate: Framerate for the output video. Default is 30.
        :return: None
        """
        input_path = os.path.join(self.frame_folder, "%d.jpeg")
        (
            ffmpeg.input(input_path, framerate=framerate)
            .output(
                os.path.join(self.temp_folder, "temp_vid.mp4"),
                vcodec="libx264",
                pix_fmt="yuv420p",
            )
            .global_args("-threads", str(self.threads))
            .run()
        )

        # Add audio to the video
        temp_video_path = os.path.join(self.temp_folder, "temp_vid.mp4")

        video = ffmpeg.input(temp_video_path)
        audio = ffmpeg.input(self.audio_path)

        (
            ffmpeg.concat(video, audio, v=1, a=1)
            .output(
                os.path.join(os.path.dirname(__file__), "final.mp4"),
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

        :return: str: Path to the frame folder.
        """
        return self.frame_folder
