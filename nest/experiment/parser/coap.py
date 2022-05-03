# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""
Runs coap commands to setup CoAP experiment
and collect throughput data
"""

from functools import partial
import copy
import json
import logging

from nest.topology_map import TopologyMap
from .runnerbase import Runner
from ..results import CoAPResults
from ...engine.coap import run_coap_client, run_coap_server

logger = logging.getLogger(__name__)

# Certain unexpected errors occuring here are captured to this file.
log_file_handler = logging.FileHandler("coap_error.log")
log_file_handler.setLevel(logging.ERROR)
logger.addHandler(log_file_handler)


class CoAPRunner(Runner):
    """
    Runs coap client and server.

    Attributes
    ----------
    default_coap_client_options : dict
        Contains default options for the client to create messages
    user_options : dict
        Contains options provided by the user
    """

    # Contains the default CoAP client options
    # Will be used to form the CoAP client options string
    # to pass to the engine client file
    # More options can be added as per requirements
    default_coap_client_options = {
        "coap_message_payload": '-m "This is the default message for CoAP"',
        "coap_request_type": "-r get",
        "coap_non_timeout": "-t 5",
    }

    # pylint: disable=too-many-arguments
    def __init__(self, ns_id, destination_ip, user_options, n_con_msgs, n_non_msgs):
        """
        Constructor to initialize the runner

        Parameters
        ----------
        ns_id : str
            network namespace to run coap from
        destination_ip : str
            the ip of server to which it has to connect
        user_options: dict
            coap options provided by user to override default
        n_con_msgs : num
            number of CON messages to be sent
        n_non_msgs : num
            number of NON messages to be sent
        """
        self.user_options = user_options
        self.n_con_msgs = n_con_msgs
        self.n_non_msgs = n_non_msgs
        super().__init__(
            ns_id, start_time=None, run_time=None, destination_ip=destination_ip
        )

    @staticmethod
    def run_server(ns_id, server_options):
        """
        Run coap server in `ns_id`

        Parameters
        ----------
        ns_id : str
            namespace to run netserver on
        server_options : str
            options provided by the user for running the server
        """
        # Check if user has provided their own server options
        if server_options is not None:
            server_options_string = server_options

        # If not, use default options
        else:
            server_options_string = '-c "This is the default resource content for CoAP"'

        # Run CoAP server
        return_code = run_coap_server(ns_id, server_options_string)
        if return_code != 0:
            ns_name = TopologyMap.get_node(ns_id).name
            logger.error("Error running coap server at %s.", ns_name)

    def run(self):
        """
        Calls engine method to run coap client
        """
        coap_client_options = copy.copy(CoAPRunner.default_coap_client_options)

        # If the user has not supplied options, take the default options
        if self.user_options is None:
            coap_client_options.pop("coap_message_payload")
        else:
            # If user has provided the request type
            if "coap_request_type" in self.user_options.keys():
                # Convert the request type string to lowercase
                coap_request_type = self.user_options["coap_request_type"].lower()
            else:
                # If user has not provided the request type, take GET
                coap_request_type = "get"

            # Check validity of request type
            if coap_request_type not in ("get", "put"):
                logger.warning("Invalid request type %s.", coap_request_type)
                logger.warning("Taking 'get' as current request type.")
                coap_request_type = "get"

            coap_client_options["coap_request_type"] = f"-r {coap_request_type}"

            # Add message payload if 'put' request
            if coap_request_type == "put":
                if (
                    "coap_message_payload" in self.user_options.keys()
                    and self.user_options["coap_message_payload"] != ""
                ):
                    coap_message_payload = (
                        '"' + self.user_options["coap_message_payload"] + '"'
                    )
                    coap_client_options[
                        "coap_message_payload"
                    ] = f"-m {coap_message_payload}"

            # Message payload should not be sent for GET request
            else:
                coap_client_options.pop("coap_message_payload")

        # Add n_con_msgs and n_non_msgs
        coap_client_options["coap_n_con_msgs"] = f"-c {self.n_con_msgs}"
        coap_client_options["coap_n_non_msgs"] = f"-n {self.n_non_msgs}"

        # Add non_timeout to coap_client_options
        if "coap_non_timeout" in self.user_options.keys():
            non_timeout = self.user_options["coap_non_timeout"]
            coap_client_options["coap_non_timeout"] = f"-t {non_timeout}"

        # Convert coap_client_options dict to string for running engine
        coap_client_options_list = list(coap_client_options.values())
        coap_client_options_string = " ".join(coap_client_options_list)

        # Run CoAP client
        super().run(
            partial(
                run_coap_client,
                self.ns_id,
                self.destination_address.get_addr(with_subnet=False),
                self.destination_address.is_ipv6(),
                coap_client_options_string,
            ),
            error_string_prefix="Running coap",
        )

    def parse(self):
        """
        Parse coap output and error from self.out and self.err
        """
        # Rewind to start of the out file and read output
        self.out.seek(0)
        raw_stats_out = self.out.read().decode()

        # Rewind to start of the err file and read errors
        self.err.seek(0)
        raw_stats_err = self.err.read().decode()

        # Errors that occur outside the usual error
        # control systems are caught here. Since those
        # errors are still written to `stderr`, `json.loads`
        # would throw an exception for them not being in the
        # JSON format.
        #
        # Hence the exception is `JSONDecodeError`.
        try:
            # Parse outputs
            parsed_stats_out = {}
            if raw_stats_out != "":
                parsed_stats_out = json.loads(raw_stats_out)

            # Parse errors
            parsed_stats_err = {}
            if raw_stats_err != "":
                parsed_stats_err = json.loads(raw_stats_err)

        except json.decoder.JSONDecodeError:
            logger.error("Unexpected JSON Error. Error dump: %s", raw_stats_err)

        # Get Destination IP address and add results to runner
        destination_ip = self.destination_address.get_addr(with_subnet=False)
        CoAPResults.add_result(
            self.ns_id,
            {destination_ip: {"output": parsed_stats_out, "error": parsed_stats_err}},
        )
