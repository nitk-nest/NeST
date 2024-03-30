# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2024 NITK Surathkal

"""
Runs commands to setup SIP experiment and collect data
"""

from functools import partial
import logging

from nest.topology_map import TopologyMap
from ..results import SipResults
from .runnerbase import Runner
from ...engine.sip import run_sip_client, run_sip_server

logger = logging.getLogger(__name__)

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods


class SipRunner(Runner):
    """
    Runs SIP client and server.

    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        ns_id,
        destination_ip,
        dst_ns,
        port,
        duration,
        scenario,
        server_xml_file,
        client_xml_file,
        callrate,
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

        """
        self.port = port
        self.duration = duration
        self.scenario = scenario
        self.server_xml_file = server_xml_file
        self.client_xml_file = client_xml_file
        self.callrate = callrate

        super().__init__(
            ns_id,
            start_time=None,
            run_time=None,
            destination_ip=destination_ip,
            dst_ns=dst_ns,
            use_named_out_file=True,
        )

    @staticmethod
    def run_server(ns_id, port, scenario, xml_file):
        """
        Run SIP server

        Parameters
        ----------
        ns_id : str
            namespace to run SIP server on
        port : int
            port to run SIP server on
        scenario : str
            Specifies the scenario to be run for the experiment.
            (uses "basic" by default)
        xml_file : Path
            Specifies the path to an XML scenario file for the SIPp test.
            (Used only when scenario is "xml")
        """

        return_code = run_sip_server(ns_id, port, scenario, xml_file)
        if return_code not in (99, 0):
            ns_name = TopologyMap.get_node(ns_id).name
            logger.error("Error running SIP server at %s.", ns_name)

    # pylint: disable=too-many-statements, too-many-branches
    def run(self):
        """
        Calls engine method to run SIP client
        """

        # Run SIP client
        super().run(
            partial(
                run_sip_client,
                self.ns_id,
                self.destination_address.get_addr(with_subnet=False),
                self.port,
                self.duration,
                scenario=self.scenario,
                xml_file=self.client_xml_file,
                callrate=self.callrate,
            ),
            error_string_prefix="Running SIP",
        )

    def parse(self):
        """
        Parse SIP output from self.out
        """
        # Rewind to start of the out file and read output
        self.out.seek(0)
        lines = self.out.readlines()

        data = []
        headers = lines[0].decode().split(";")

        for line in lines[1:]:
            values = line.decode().split(";")
            values.remove("\n")
            data.append(dict(zip(headers, values)))

        SipResults.add_result(
            self.ns_id,
            data[-1],
        )
