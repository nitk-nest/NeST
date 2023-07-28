# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2024 NITK Surathkal

"""MPEG-DASH Encoder"""

from pathlib import Path
import logging
import re
import shutil

from nest.engine.exec import exec_exp_commands, exec_subprocess_with_live_output
from nest.engine.util import is_dependency_installed

logger = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=too-few-public-methods
class MpegDashEncoder:
    """
    Contains the configuration settings and script to encode a video.
    """

    mpeg_dash_encoded_chunks_path_list = []

    def __init__(
        self,
        gop_size: int = 15,
        fps: int = 30,
        video_codec: str = "libx264",
        pixel_format: str = "yuv420p",
        audio_codec: str = "aac",
        audio_bitrate: str = "128k",
        segment_duration: int = 1,
        aspect_ratio: str = "16/9",
        video_stream_info: list = None,
    ):
        """
        Constructor to initialize the MPEG-DASH encoder

        Parameters
        ----------
        gop_size : int
            Group of pictures (GOP) size
        fps : int
            Frame rate (per second)
        video_codec: str
            Name of the video codec to be used
        pixel_format: str
            Type of pixel format (Supported formats can be viewed
            here: https://github.com/gpac/gpac/wiki/filters_properties#pixel-formats)
        audio_codec: str
            Name of the audio codec to be used
        audio_bitrate: str
            Amount of audio bitrate required
        segment_duration: int
            Duration of each encoded MPEG-DASH segment
        aspect_ratio: str
            Ratio between the video's width and height.
        video_stream_info: list
            List containing JSON objects that contain video resolution and bitrate.
        """
        if not is_dependency_installed("gpac"):
            raise RuntimeError("Encoding Failed! gpac is not installed!")

        if not isinstance(gop_size, int):
            raise ValueError("gop_size is supposed to be an integer value.")

        if not isinstance(fps, int):
            raise ValueError("fps is supposed to be an integer value.")

        if not isinstance(segment_duration, int):
            raise ValueError("segment_duration is supposed to be an integer value")

        if video_stream_info is None:
            video_stream_info = [
                {"resolution": "256x144", "bitrate": "50K"},
                {"resolution": "427x240", "bitrate": "100K"},
                {"resolution": "640x360", "bitrate": "400K"},
                {"resolution": "854x480", "bitrate": "750K"},
                {"resolution": "1280x720", "bitrate": "2.5M"},
                {"resolution": "1920x1080", "bitrate": "6M"},
            ]

        resolution_pattern = r"\d+x\d+"
        bitrate_pattern = r"^\d+(\.\d+)?[KkMm]"
        aspect_ratio_pattern = r"^\d+/\d+$"

        if not re.match(bitrate_pattern, audio_bitrate):
            raise ValueError(
                '"bitrate" for audio is not in the specified format. i.e. "2.5M" or "5K".'
            )

        if not re.match(aspect_ratio_pattern, aspect_ratio):
            raise ValueError(
                'Aspect Ratio is not in the specified format. i.e. "<width>/<height>". E.g. "16/9"'
            )

        for video_repr in video_stream_info:
            if ("resolution" not in video_repr) or ("bitrate" not in video_repr):
                raise KeyError('"resolution" or "bitrate" key not found')

            if not re.match(resolution_pattern, video_repr["resolution"]):
                raise ValueError(
                    '''"resolution" is not in the specified format.
                    i.e. "<width>x<height>". E.g. "1920x1080"'''
                )

            if not re.match(bitrate_pattern, video_repr["bitrate"]):
                raise ValueError(
                    '"bitrate" for video is not in the specified format. i.e. "2.5M" or "5K".'
                )

        self.gop_size = gop_size
        self.fps = fps
        self.video_codec = video_codec
        self.pixel_format = pixel_format
        self.audio_codec = audio_codec
        self.audio_bitrate = audio_bitrate
        self.segment_duration = segment_duration
        self.aspect_ratio = aspect_ratio
        self.video_stream_info = video_stream_info

    def encode_video(
        self, input_video_path: Path, output_path: Path, overwrite: bool = False
    ):
        """
        Encodes the file corresponding to `input_video_path` and
        stores the encoded chunks in the `output_path`.

        Parameters
        ----------
        input_video_path: Path
            Path of the input video file
        output_path: Path
            Path to store the encoded chunks in.
        overwrite: bool
            If 'True' then the 'output_path' directory is emptied and then chunks are stored.

        Returns
        -------
        int
            Return code recieved after the encoding process terminates
        """

        if not Path.exists(input_video_path):
            logger.warning("The path '%s' does not exist.", str(input_video_path))
            logger.warning("Using a sample video from the internet for encoding.")

            if not is_dependency_installed("wget"):
                raise RuntimeError(
                    "Error downloading sample video! wget is not installed!"
                )

            input_video_url = (
                "https://commondatastorage.googleapis.com/"
                "gtv-videos-bucket/sample/ForBiggerEscapes.mp4"
            )

            download_dir = "/tmp/mpeg-dash-sample-video/"
            exec_subprocess_with_live_output(
                f"wget {input_video_url} -P {download_dir} -nc -q --show-progress"
            )

            input_video_path = (
                download_dir + input_video_url.rsplit("/", maxsplit=1)[-1]
            )

        MpegDashEncoder.mpeg_dash_encoded_chunks_path_list.append(output_path)

        if Path.exists(output_path) and any(
            file.suffix == ".mpd" for file in output_path.iterdir()
        ):
            if overwrite is False:
                logger.warning(
                    "The path '%s' already contains an MPD file.", str(output_path)
                )
                logger.warning(
                    "Utilizing the pre-existing MPD file for MPEG-DASH streaming."
                )
                return 0
            shutil.rmtree(output_path)
            logger.warning(
                "Overwriting the files in the directory '%s' .", str(output_path)
            )
        else:
            output_path.mkdir(parents=True, exist_ok=True)

        cmd_string = f" gpac -i {input_video_path}:FID=srcFile:FPS={self.fps} "

        # Setting video encoding parameters
        for i in range(len(self.video_stream_info)):
            cmd_string += f"ffsws:osize={self.video_stream_info[i]['resolution']}"
            cmd_string += f":osar={self.aspect_ratio}"
            cmd_string += (
                f":SID=srcFile:FID={self.video_stream_info[i]['resolution']}_res"
            )
            cmd_string += f" enc:c={self.video_codec}"
            cmd_string += f":fintra=1:bitrate={self.video_stream_info[i]['bitrate']}"
            cmd_string += f":cgop=true:gop={self.gop_size}"
            cmd_string += (
                f":SID={self.video_stream_info[i]['resolution']}_res:FID=EV{i} "
            )

        # Setting audio encoding parameters
        cmd_string += f"c={self.audio_codec}:SID=srcFile"
        cmd_string += f":FID=EA:bitrate={self.audio_bitrate} "
        cmd_string += f"-o {output_path}/manifest.mpd:gpac"
        cmd_string += ":SID="
        for i in range(len(self.video_stream_info)):
            cmd_string += f"EV{i},"
        cmd_string += f"EA:segdur={self.segment_duration}:cdur=0.5"
        cmd_string += (
            ":profile=dashavc264.live:title='MPEG-DASH Application (NITK-NeST)'"
        )

        logger.info(
            "Video encoding started. Please be patient. This may take a while.."
        )

        status = exec_exp_commands(cmd_string)

        if status == 0:
            logger.info("Video encoding completed successfully!")
        else:
            logger.error("Video encoding failed!")

        return status
