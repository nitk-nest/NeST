# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

""" Runs iperf command to setup udp flows """

from time import sleep
from .runnerbase import Runner
from ...engine.iperf import run_iperf_server, run_iperf_client


class IperfRunner(Runner):
    """
    Runs iperf client and server. Currently being used
    for udp flows only

    Attributes
    ----------
    ns_id : str
        network namespace to run iperf from
    """

    def __init__(self, ns_id):
        """
        Constructor to initalize the runner

        Parameters
        ----------
        ns_id : str
            network namespace to run iperf from
        """
        self.ns_id = ns_id
        super().__init__()

    def run_server(self):
        """
        calls engine method to run iperf server
        """
        run_iperf_server(self.ns_id)

    # pylint: disable=invalid-name
    # pylint: disable=too-many-arguments
    def run_client(self, destination, start_time, run_time, flows, bw):
        """
        calls engine method to run iperf client

        Parameters
        ----------
        destination : str
            the ip of server to which it has to connect
        start_time : num
            start time of the flow
        run_time : num
            test duration
        flows : int
            number of parallel flows
        bw : int
            target bandwidth of the udp flow in mbits
        """
        if start_time != 0:
            sleep(start_time)
        run_iperf_client(self.ns_id, destination, run_time, flows, bw)
