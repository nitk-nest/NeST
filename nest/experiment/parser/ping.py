# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Runs and provides RTT output from ping command"""

import re
from time import sleep
from functools import partial
from nest.experiment.interrupts import handle_keyboard_interrupt
from .runnerbase import Runner
from ..results import PingResults
from ...engine.ping import run_exp_ping


class PingRunner(Runner):
    """
    Runs ping command and parses statistics from its output

    Attributes
    ----------
    ns_id : str
        network namespace to run netperf from
    destination_ip : str
        IP address of the destination namespace
    start_time : num
        time at which netperf is to run
    run_time : num
        total time to run netperf for
    """

    # pylint: disable=too-many-arguments
    def __init__(self, ns_id, destination_ip, start_time, run_time, dst_ns):
        """
        Constructor to initialize ping runner

        Parameters
        ----------
        ns_id : str
            network namespace to run ping from
        destination_ip : str
            IP address of the destination namespace
        start_time : num
            time at which netperf is to run
        run_time : num
            total time to run netperf for
        dst_ns : str
            destination network namespace of ping
        """
        super().__init__(ns_id, start_time, run_time, destination_ip, dst_ns)

    # pylint: disable=arguments-differ
    def run(self):
        """
        Runs ping at t=`self.start_time`
        """
        if self.start_time > 0:
            sleep(self.start_time)

        super().run(
            partial(
                run_exp_ping,
                self.ns_id,
                self.destination_address.get_addr(with_subnet=False),
                self.run_time,
                self.destination_address.is_ipv6(),
            ),
            error_string_prefix="Collecting latency",
        )

    @handle_keyboard_interrupt
    def parse(self):
        """
        parses the RTT from `self.out`
        """
        self.out.seek(0)  # rewind to start of the temp file
        raw_stats = self.out.read().decode()

        pattern = r"\[(?P<timestamp>\d+\.\d+)\].*time=(?P<rtt>\d+(\.\d+)?)"
        timestamps_and_rtts = [
            (match.group("timestamp"), match.group("rtt"))
            for match in re.finditer(pattern, raw_stats)
        ]

        # List storing collected stats
        # First item as "meta" item with user given information
        stats_list = [self.get_meta_item()]

        for (timestamp, rtt) in timestamps_and_rtts:
            stats_list.append({"timestamp": timestamp, "rtt": rtt})

        stats_dict = {self.destination_address.get_addr(with_subnet=False): stats_list}

        PingResults.add_result(self.ns_id, stats_dict)
