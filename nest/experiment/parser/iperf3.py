# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

""" Runs iperf command to setup UDP flows """

from time import sleep
from functools import partial
import copy
import json
import logging

from nest.topology_map import TopologyMap
from ..results import Iperf3Results
from .runnerbase import Runner
from ...engine.iperf3 import run_iperf_server, run_iperf_client

logger = logging.getLogger(__name__)


class Iperf3Runner(Runner):
    """
    Runs iperf client and server. Currently being used
    for UDP flows only

    Attributes
    ----------
    ns_id : str
        network namespace to run iperf from
    """

    # fmt: off

    default_iperf3_options = {
        "interval": "-i 0.2",       # Generate interim results every INTERVAL seconds
        "json": "--json",           # Get output in easily parsable JSON format
        "testlen": "-t 10",         # Length of test (NOTE: Default 10s)
        "protocol": "--udp",        # Transport protocol to use (TODO: Add support for TCP as well)
        "n_flows": "-P 1",          # Number of parallel flows (NOTE: Default 1)
        "bitrate": "-b 1M"          # Target bitrate (NOTE: Default 1 Mbit/sec)
    }

    # fmt: on

    # pylint: disable=too-many-arguments
    def __init__(
        self, ns_id, destination_ip, bandwidth, n_flows, start_time, run_time, dst_ns
    ):
        """
        Constructor to initialize the runner

        Parameters
        ----------
        ns_id : str
            network namespace to run iperf3 from
        destination : str
            the ip of server to which it has to connect
        bandwidth : int
            target bandwidth of the UDP flow in mbits
        n_flows : int
            number of parallel flows
        start_time : num
            start time of the flow
        run_time : num
            test duration
        dst_ns: str
            network namespace to run iperf3 server from
        """
        self.bandwidth = bandwidth
        self.n_flows = n_flows
        super().__init__(ns_id, start_time, run_time, destination_ip, dst_ns)

    # Should this be placed somewhere else?
    @staticmethod
    def run_server(ns_id):
        """
        Run iperf server in `ns_id`

        Parameters
        ----------
        ns_id : str
            namespace to run netserver on
        """
        return_code = run_iperf_server(ns_id)
        if return_code != 0:
            ns_name = TopologyMap.get_namespace(ns_id)["name"]
            logger.error("Error running iperf3 server at %s.", ns_name)

    def run(self):
        """
        calls engine method to run iperf client
        """
        iperf3_options = copy.copy(Iperf3Runner.default_iperf3_options)

        # Set run time
        iperf3_options["testlen"] = f"-t {self.run_time}"

        # Set number of parallel flows
        iperf3_options["n_flows"] = f"-P {self.n_flows}"

        # Set target bitrate
        iperf3_options["bitrate"] = f"-b {self.bandwidth}"

        # Convert iperf3_options dict to string
        iperf3_options_list = list(iperf3_options.values())
        iperf3_options_string = " ".join(iperf3_options_list)

        if self.start_time != 0:
            sleep(self.start_time)

        super().run(
            partial(
                run_iperf_client,
                self.ns_id,
                iperf3_options_string,
                self.destination_address.get_addr(with_subnet=False),
                self.destination_address.is_ipv6(),
            ),
            error_string_prefix="Running iperf3",
        )

    def parse(self):
        """
        Parse iperf3 output from self.out
        """
        self.out.seek(0)  # rewind to start of the temp file
        raw_stats = self.out.read().decode()

        # Iperf3 already gives output in JSON format, so we parse
        # into a dictionary
        parsed_stats = json.loads(raw_stats)

        # Extract from useful connection info from parsed data
        # Useful for diffrentiating between flows
        start_timestamp = parsed_stats["start"]["timestamp"]["timesecs"]
        connection_info = {}

        for conn in parsed_stats["start"]["connected"]:
            connection_info[conn["socket"]] = {
                "local_host": conn["local_host"],
                "local_port": conn["local_port"],
                "remote_host": conn["remote_host"],
                "remote_port": conn["remote_port"],
            }

        # Convert iperf3 JSON data into our own JSON format (similar
        # to netperf), so that plotter code can be reused

        stats_dict_list = {}
        for socket in connection_info:
            local_port = connection_info[socket]["local_port"]
            stats_dict_list[local_port] = [self.get_meta_item()]

        if len(stats_dict_list) > 1:
            stats_dict_list["sum"] = [self.get_meta_item()]

        for interval in parsed_stats["intervals"]:
            for stream in interval["streams"]:
                socket = stream["socket"]
                local_port = connection_info[socket]["local_port"]
                stats_dict_list[local_port].append(
                    self._extract_from_ipref3_stream(start_timestamp, stream)
                )

            if len(stats_dict_list) > 1:
                sum_stream = interval["sum"]
                stats_dict_list["sum"].append(
                    self._extract_from_ipref3_stream(start_timestamp, sum_stream)
                )

        destination_ip = self.destination_address.get_addr(with_subnet=False)
        Iperf3Results.add_result(self.ns_id, {destination_ip: stats_dict_list})

    def _extract_from_ipref3_stream(self, start_timestamp, stream):
        """
        Convert information in iperf3 stream into required
        dictionary format
        """
        return {
            "timestamp": str(stream["start"] + start_timestamp),
            "sending_rate": str(stream["bits_per_second"] / 1e6),
            "duration": str(stream["seconds"]),
            "bytes": str(stream["bytes"]),
            "packets": str(stream["packets"]),
        }
