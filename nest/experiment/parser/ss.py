# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
Runs ss command and parses socket stats from
its output
"""

import os
import re
from functools import partial
from nest.experiment.interrupts import handle_keyboard_interrupt
from ..results import SsResults
from .runnerbase import Runner
from ...engine.iterators import run_ss


class SsRunner(Runner):
    """
    Runs ss command and stores and parses the output

    Attributes
    ----------
    iterator : str
        absolute path of the ss iterator script
    param_list: list(str)
        list of parameters to be parsed
    ns_id : str
        network namespace to run ss from
    destination_ip : str
        IP address of the destination namespace
    start_time : num
        time at which ss is to be run
    run_time : num
        total time to run ss for
    """

    iterator = os.path.realpath(os.path.dirname(__file__)) + "/iterators/ss.sh"
    param_list = [
        "cwnd",
        "rwnd",
        "rtt",
        "ssthresh",
        "rto",
        "delivery_rate",
        "pacing_rate",
    ]

    # pylint: disable=too-many-arguments
    def __init__(
        self, ns_id, destination_ip, start_time, run_time, dst_ns, ss_filter=""
    ):
        """
        Constructor to initialize ss runner

        Parameters
        ----------
        ns_id : str
            network namespace to run ss from
        destination_ip : str
            IP address of the destination namespace
        start_time : num
            time at which ss is to be run
        run_time : num
            total time to run ss for
        dst_ns : str
            destination network namespace of ss
        ss_filter : str
            to filter output from specific connections.
        """
        self.filter = ss_filter
        super().__init__(ns_id, start_time, run_time, destination_ip, dst_ns)

    def run(self):
        """
        Runs the ss iterator
        """
        super().run(
            partial(
                run_ss,
                self.ns_id,
                SsRunner.iterator,
                self.destination_address.get_addr(with_subnet=False),
                self.run_time,
                f'"{self.filter}"',
                self.start_time,
                self.destination_address.is_ipv6(),
            ),
            error_string_prefix="Collecting socket stats",
        )

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    @handle_keyboard_interrupt
    def parse(self):
        """
        parses the required data from `self.out`
        """
        stats_dict_list = {}

        self.out.seek(0)  # rewind to start of the temp file

        # See `iterators/ss.h` for output format
        raw_stats = self.out.read().decode().split("---")
        destination_ip = self.destination_address.get_addr(with_subnet=False)

        # iperf3 creates 1 additional connection (apart from the N connections
        # for the N flows specified) every time you run the iperf3 command.
        # This additional connection is used by iperf3 API iperf for collecting,
        # sending, and printing intermediate results at specific intervals
        # (https://github.com/esnet/iperf/blob/master/src/iperf_api.c#L3269).
        # The ss parser will split each of the raw_stat data in new lines,
        # and get rid of (ignore) the data from that 1 additional connection
        # altogether based on the 'ato' parameter (which is present only in the
        # additional connection that we do not want to collect stats from).
        for raw_stat in raw_stats[:-1]:

            stats = raw_stat.strip().split("\n")
            timestamp = stats[0].split(":")[-1]
            ports_info = []
            statistics_data = []

            for i, row in enumerate(stats[2:]):
                if i % 2 == 0:
                    ports_info.append(row.strip())
                else:
                    statistics_data.append(row.strip())
            assert len(ports_info) == len(statistics_data)

            for i in range(len(ports_info)):
                # means that this is additional info entries and this data isn't required
                if "ato" in statistics_data[i]:
                    continue
                each_ports_info = ports_info[i].split()

                # means that this entry was not meant for this stat collection
                if each_ports_info[-1].split(":")[0] != destination_ip:
                    continue

                dst_port = each_ports_info[-1].split(":")[-1]

                if dst_port not in stats_dict_list:
                    stats_dict_list[dst_port] = [self.get_meta_item()]
                stats_dict_list[dst_port].append({"timestamp": timestamp})

                for param in SsRunner.param_list:
                    pattern = (
                        r"\s"
                        + re.escape(param)
                        + r"[\s:](?P<value>\w+\.?\w*(?:[\/\,]\w+\.?\w*)*)\s"
                    )
                    # result list stores all the string that is matched by the `pattern`
                    try:
                        param_value = (
                            re.search(pattern, statistics_data[i]).group(1).strip()
                        )
                    except AttributeError:
                        continue

                    if param_value.endswith("bps"):
                        param_value = self.convert_to(param_value)
                    try:
                        # RTT has both average and RTT deviation separated by a /
                        if param == "rtt":
                            avg_rtt = param_value.split("/")[0]
                            dev_rtt = param_value.split("/")[1]
                            stats_dict_list[dst_port][-1]["rtt"] = avg_rtt
                            stats_dict_list[dst_port][-1]["dev_rtt"] = dev_rtt
                        else:
                            stats_dict_list[dst_port][-1][param] = param_value
                    except TypeError:
                        pass

        destination_ip = self.destination_address.get_addr(with_subnet=False)
        SsResults.add_result(self.ns_id, {destination_ip: stats_dict_list})

    @staticmethod
    def convert_to(param_value, unit_out="Mbps"):
        """
        Converts parameter value to specified unit [For bit per second]
        """
        converter = {"bps": 1, "Kbps": 1e3, "Mbps": 1e6, "Gbps": 1e9}

        # Extract value and unit
        unit_in = re.sub(r"^\d*\.?\d*", "", param_value)
        extracted_param_value = float(re.sub(r"[A-Za-z]*", "", param_value))

        converted_param_value = str(
            extracted_param_value * converter[unit_in] / converter[unit_out]
        )
        return converted_param_value
