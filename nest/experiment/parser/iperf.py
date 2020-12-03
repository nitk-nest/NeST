# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

""" Runs iperf command to setup UDP flows """

from time import sleep
from .runnerbase import Runner
from ...engine.iperf import run_iperf_server, run_iperf_client

# NOTE: Uses iperf3 command
class IperfRunner(Runner):
    """
    Runs iperf client and server. Currently being used
    for UDP flows only

    Attributes
    ----------
    ns_id : str
        network namespace to run iperf from
    """

    # pylint: disable=too-many-arguments
    def __init__(self, ns_id, destination_ip, bandwidth, n_flows, start_time, run_time):
        """
        Constructor to initialize the runner

        Parameters
        ----------
        ns_id : str
            network namespace to run iperf from
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
        """
        self.ns_id = ns_id
        self.destination_ip = destination_ip
        self.bandwidth = bandwidth
        self.n_flows = n_flows
        super().__init__(start_time, run_time)

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
        run_iperf_server(ns_id)

    # This method should call super().run
    def run(self):
        """
        calls engine method to run iperf client
        """
        if self.start_time != 0:
            sleep(self.start_time)
        run_iperf_client(self.ns_id, self.destination_ip,
                         self.run_time, self.n_flows, self.bandwidth)
