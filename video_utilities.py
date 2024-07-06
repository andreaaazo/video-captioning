import ffmpeg


class VideoUtilities:
    """
    VideoUtilities provides various video processing utilities.

    :param [str] video_path: Path to the input video file.
    """

    def __init__(self, video_path):
        self.video_path = video_path

    def get_duration(self):
        """
        get_duration fetches the duration of the video.

        :return: Duration of the video in seconds.
        """
        probe = ffmpeg.probe(self.video_path)
        duration = float(probe["format"]["duration"])
        return duration

    def get_resolution(self):
        """
        get_resolution retrieves the resolution of the video.

        :return: Tuple containing (width, height) of the video.
        """
        probe = ffmpeg.probe(self.video_path)
        video_stream = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
            None,
        )
        width = int(video_stream["width"])
        height = int(video_stream["height"])
        return width, height

    def trim_video(self, start_time, end_time, output_path):
        """
        trim_video trims the video to the specified timestamps.

        :param [str] start_time: Start time to trim the video (format: 'HH:MM:SS').
        :param [str] end_time: End time to trim the video (format: 'HH:MM:SS').
        :param [str] output_path: Path to save the trimmed video.
        :return: None
        """
        ffmpeg.input(self.video_path, ss=start_time, to=end_time).output(
            output_path
        ).run()
