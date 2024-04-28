# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

"""
Runs commands to setup MPEG-DASH experiment and collect data
"""

from functools import partial
import logging
from enum import Enum
from threading import Lock

from nest.topology_map import TopologyMap
from ..results import MpegDashResults
from .runnerbase import Runner
from ...engine.mpeg_dash import run_mpeg_dash_client, run_mpeg_dash_http_server
from ..pack import Pack

logger = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
class MpegDashLogExtractor:
    """
    Contains information related to a single log entry.
    """

    class LogType(Enum):
        """
        An enum depicting the type of the log.
        """

        NONE = "None"
        AUDIO = "Audio"
        VIDEO = "Video"

    def __init__(self, words_in_line):
        self.log_type = MpegDashLogExtractor.LogType.NONE
        self.bitrate_switch = 0
        self.time = 0
        self.segment_size = 0
        self.throughput = 0
        self.bitrate_level = 0
        self.bitrate = 0
        self.buffer = 0
        self.__extract_info(words_in_line)

    def __extract_info(self, words_in_line):
        for i in range(0, len(words_in_line)):
            if words_in_line[i] == "AS#1":
                # Assuming AS1 is Adaptation set for audio
                self.log_type = MpegDashLogExtractor.LogType.AUDIO
            elif words_in_line[i] == "AS#2":
                # Assuming AS2 is Adaptation set of videos
                self.log_type = MpegDashLogExtractor.LogType.VIDEO
            elif words_in_line[i] == "changed" and words_in_line[i + 1] == "quality":
                self.bitrate_switch = 1
                if self.log_type in (
                    MpegDashLogExtractor.LogType.VIDEO,
                    MpegDashLogExtractor.LogType.AUDIO,
                ):
                    # Setting Bitrate switching parameters
                    self.bitrate_level = int(words_in_line[6])
                break
            elif words_in_line[i] == "got":
                self.time = float(words_in_line[8])
                self.throughput = float(words_in_line[11])
                self.segment_size = float(words_in_line[15])
                self.bitrate = float(words_in_line[19])
                self.bitrate_level = int(
                    words_in_line[21][: len(words_in_line[21]) - 1]
                )
                self.buffer = int(words_in_line[25])
                break

    def __str__(self):
        log_data = []
        log_data.append(("Log Type", self.log_type))
        log_data.append(("Bitrate-switch", self.bitrate_switch))
        log_data.append(("Time", self.time))
        log_data.append(("Segment size", self.segment_size))
        log_data.append(("Throughput", self.throughput))
        log_data.append(("Bitrate-level", self.bitrate_level))
        log_data.append(("Bitrate", self.bitrate))
        log_data.append(("Buffer", self.buffer))
        return " " + str(log_data)


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
class MpegDashRunner(Runner):
    """
    Runs MPEG-DASH client and server.

    """

    lock = Lock()

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        ns_id,
        destination_ip,
        dst_ns,
        port,
        encoded_chunks_path,
        duration,
        player,
        enable_audio_playback,
        additional_player_options,
    ):
        """
        Constructor to initialize the runner

        Parameters
        ----------
        ns_id : str
            network namespace of the client
        destination_ip : str
            the ip of server to which it has to connect
        dst_ns : str
            network namespace of the server
        port: int
            the port number of the server at which it is running
        encoded_chunks_path : Path
            The path where the encoded chunks are present.
        duration : int
            Number of seconds for which experiment has to be run
        player: str
            The media player to be used.
        enable_audio_playback: bool
            Enable/disable audio playback
        additional_player_options : string
            User specified options for the video player
        """
        self.port = port
        self.encoded_chunks_path = encoded_chunks_path
        self.duration = duration
        self.player = player
        self.enable_audio_playback = enable_audio_playback
        self.additional_player_options = additional_player_options
        super().__init__(
            ns_id,
            start_time=None,
            run_time=None,
            destination_ip=destination_ip,
            dst_ns=dst_ns,
        )
        self.audio_logs = []
        self.video_logs = []
        self.audio_info = {
            "bitrate_switches": 0,
            "average_bitrate": 0,
            "average_throughput": 0,
            "average_buffer": 0,
            "average_rtt": 0,
        }
        self.video_info = {
            "bitrate_switches": 0,
            "average_bitrate": 0,
            "average_throughput": 0,
            "average_buffer": 0,
            "average_rtt": 0,
        }

    @staticmethod
    def run_server(ns_id, port, encoded_chunks_path):
        """
        Run MPEG-DASH server in `ns_id`

        Parameters
        ----------
        ns_id : str
            namespace to run MPEG-DASH server on
        port : int
            port to run MPEG-DASH server on
        encoded_chunks_path : Path
            The path where the encoded chunks are present.
        """

        # Run mpeg-dash server
        return_code = run_mpeg_dash_http_server(ns_id, port, encoded_chunks_path)
        if return_code != 0:
            ns_name = TopologyMap.get_node(ns_id).name
            logger.error("Error running MPEG-DASH server at %s.", ns_name)

    # pylint: disable=too-many-statements, too-many-branches
    def run(self):
        """
        Calls engine method to run MPEG-DASH client
        """

        # Run MPEG-DASH client
        super().run(
            partial(
                run_mpeg_dash_client,
                self.ns_id,
                self.destination_address.get_addr(with_subnet=False),
                self.port,
                self.duration,
                player=self.player,
                enable_audio_playback=self.enable_audio_playback,
                additional_player_options=self.additional_player_options,
            ),
            error_string_prefix="Running MPEG-DASH",
        )

    # pylint: disable=too-many-locals
    def parse(self):
        """
        Parse MPEG-DASH output from self.err
        """
        if self.player == "vlc":
            return

        # Rewind to start of the err file and read output
        self.err.seek(0)

        # The dump file name is of the form: 'mpeg_dash_gpac_{client_ns}_to_{server_ns}_
        # ({server_ip}:{server_port}).log' The raw GPAC logs are dumped to this file
        # incase the user wants to parse the logs manually.
        src_ns_name = TopologyMap.get_node(self.ns_id).name
        dst_ns_name = TopologyMap.get_node(self.dst_ns).name

        server_ip_port = (
            self.destination_address.get_addr(with_subnet=False) + ":" + str(self.port)
        )

        dump_filename = "mpeg_dash_gpac_"
        dump_filename += f"{src_ns_name}_to_"
        dump_filename += f"{dst_ns_name}_({server_ip_port}).log"
        Pack.dump_file(dump_filename, self.err.read().decode())

        results_json = {server_ip_port: {}}

        self.err.seek(0)
        file_lines = self.err.readlines()

        lines = []
        for file_line in file_lines:
            lines.extend(file_line.splitlines())

        for line in lines:
            words = list(line.decode().split())
            if (
                len(words) > 1
                and words[0] == "[DASH]"
                and (words[1] == "AS#1" or words[1] == "AS#2")
                and (words[4] != "done")
            ):
                log = MpegDashLogExtractor(words)
                if log.log_type == MpegDashLogExtractor.LogType.AUDIO:
                    self.audio_logs.append(log)
                if log.log_type == MpegDashLogExtractor.LogType.VIDEO:
                    self.video_logs.append(log)

        video_stats_list = [{"server_node": TopologyMap.get_node(self.dst_ns).name}]
        audio_stats_list = [
            {
                "server_node": TopologyMap.get_node(self.dst_ns).name,
                "audio_enabled": False,
            }
        ]
        results_json[server_ip_port]["audio"] = audio_stats_list

        # Obtaining statistics from video logs
        counter = 0
        for log in self.video_logs:
            if log.bitrate_switch:
                self.video_info["bitrate_switches"] += 1
            else:
                counter += 1
                self.video_info["average_bitrate"] += log.bitrate
                self.video_info["average_throughput"] += log.throughput
                self.video_info["average_buffer"] += log.buffer
                self.video_info["average_rtt"] += log.time

        self.video_info["average_bitrate"] /= max(1, counter)
        self.video_info["average_throughput"] /= max(1, counter)
        self.video_info["average_buffer"] /= max(1, counter)
        self.video_info["average_rtt"] /= max(1, counter)

        # Formatting video statistics into JSON
        chunk_number = 0
        for log in self.video_logs:
            if not log.bitrate_switch:
                video_stats_list.append(
                    {
                        "chunk_number": chunk_number,
                        "bitrate": log.bitrate,
                        "bitrate_level": log.bitrate_level,
                        "throughput": log.throughput,
                        "buffer": log.buffer,
                        "rtt": log.time,
                    }
                )
                chunk_number += 1

        video_stats_summary = {
            "number_of_bitrate_switches": self.video_info["bitrate_switches"],
            "average_bitrate": self.video_info["average_bitrate"],
            "average_throughput": self.video_info["average_throughput"],
            "average_buffer": self.video_info["average_buffer"],
            "average_rtt": self.video_info["average_rtt"],
        }

        log_string = "### Video Stream Information ### \n"
        log_string += f"\t ### Client {src_ns_name} to "
        log_string += f"Server {dst_ns_name} "
        log_string += f"({server_ip_port}) ###\n"
        log_string += "\t Number of bitrate switches: "
        log_string += f"{video_stats_summary['number_of_bitrate_switches']} \n"
        log_string += "\t Average Bitrate: "
        log_string += f"{video_stats_summary['average_bitrate']:.2f} Kbps \n"
        log_string += "\t Average Throughput: "
        log_string += f"{video_stats_summary['average_throughput']:.2f} Kbps \n"
        log_string += "\t Average Buffer: "
        log_string += f"{video_stats_summary['average_buffer']:.2f} ms \n"
        log_string += "\t Average RTT: "
        log_string += f"{video_stats_summary['average_rtt']:.2f} s \n\n"

        results_json[server_ip_port]["video"] = video_stats_list
        results_json[server_ip_port]["video_summary"] = video_stats_summary

        if self.enable_audio_playback is True:
            # Obtaining statistics from audio logs
            counter = 0
            for log in self.audio_logs:
                if log.bitrate_switch:
                    self.audio_info["bitrate_switches"] += 1
                else:
                    counter += 1
                    self.audio_info["average_bitrate"] += log.bitrate
                    self.audio_info["average_throughput"] += log.throughput
                    self.audio_info["average_buffer"] += log.buffer
                    self.audio_info["average_rtt"] += log.time

            self.audio_info["average_bitrate"] /= max(1, counter)
            self.audio_info["average_throughput"] /= max(1, counter)
            self.audio_info["average_buffer"] /= max(1, counter)
            self.audio_info["average_rtt"] /= max(1, counter)

            # Formatting audio statistics into JSON
            chunk_number = 0
            for log in self.audio_logs:
                if not log.bitrate_switch:
                    audio_stats_list.append(
                        {
                            "chunk_number": chunk_number,
                            "bitrate": log.bitrate,
                            "bitrate_level": log.bitrate_level,
                            "throughput": log.throughput,
                            "buffer": log.buffer,
                            "rtt": log.time,
                        }
                    )
                    chunk_number += 1

            audio_stats_summary = {
                "number_of_bitrate_switches": self.audio_info["bitrate_switches"],
                "average_bitrate": self.audio_info["average_bitrate"],
                "average_throughput": self.audio_info["average_throughput"],
                "average_buffer": self.audio_info["average_buffer"],
                "average_rtt": self.audio_info["average_rtt"],
            }

            log_string += "\t ### Audio Stream Information ### \n"
            log_string += f"\t ### Client {src_ns_name} to "
            log_string += f"Server {dst_ns_name} "
            log_string += f"({server_ip_port}) ###\n"
            log_string += "\t Number of bitrate switches: "
            log_string += f"{audio_stats_summary['number_of_bitrate_switches']} \n"
            log_string += "\t Average Bitrate: "
            log_string += f"{audio_stats_summary['average_bitrate']:.2f} Kbps \n"
            log_string += "\t Average Throughput: "
            log_string += f"{audio_stats_summary['average_throughput']:.2f} Kbps \n"
            log_string += "\t Average Buffer: "
            log_string += f"{audio_stats_summary['average_buffer']:.2f} ms \n"
            log_string += "\t Average RTT: "
            log_string += f"{audio_stats_summary['average_rtt']:.2f} s \n"

            audio_stats_list[0]["audio_enabled"] = True

            results_json[server_ip_port]["audio"] = audio_stats_list
            results_json[server_ip_port]["audio_summary"] = audio_stats_summary

        with MpegDashRunner.lock:
            logger.info(log_string)
        MpegDashResults.add_result(self.ns_id, results_json)
