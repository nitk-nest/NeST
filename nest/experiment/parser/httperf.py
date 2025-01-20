# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""
Runs HTTP commands to setup HTTP experiment
and collect throughput data
"""

from functools import partial
import logging
import re
from nest.engine.httperf import run_http_client, run_http_server
from nest.experiment.results import HTTPResults
from nest.topology_map import TopologyMap
from .runnerbase import Runner

logger = logging.getLogger(__name__)


class HTTPRunner(Runner):
    """
    Runs HTTP client and server.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, ns_id, destination_ip, port, num_conns, rate, http_flow_options):
        """
        Constructor to initialize the runner

        Parameters
        ----------
        ns_id : str
            network namespace of the client
        destination_ip : str
            the ip of the HTTP server
        port : num
            port number of the server at which the it is running
        http_flow_options: dict
            httperf customizable options provided by user
        num_conns : num
            number of connections to be established bw client and server
        rate : num
            number of connections to be made by the client to the server per second
        """
        self.port = port
        self.num_conns = num_conns
        self.rate = rate
        self.http_flow_options = http_flow_options
        super().__init__(
            ns_id, start_time=None, run_time=None, destination_ip=destination_ip
        )

    @staticmethod
    def run_http_server(ns_id, port):
        """
        Run http server in `ns_id` on `port`

        Parameters
        ----------
        ns_id : str
            namespace to run http server on
        port : num
            port to run http server on
        """
        return_code = run_http_server(ns_id, port)
        if return_code != 0:
            ns_name = TopologyMap.get_node(ns_id).name
            logger.error("Error running coap server at %s.", ns_name)

    def run(self):
        """
        Calls engine method to run http client
        """
        # If user has not supplied the http flow options
        if self.http_flow_options is not None:
            # Creating the options string for running the HTTP client
            if (
                "num-calls" in self.http_flow_options.keys()
                and self.http_flow_options["num-calls"] != ""
            ):
                client_content = self.http_flow_options["num-calls"]
                client_options = f"--num-calls={client_content}"
            if (
                "timeout" in self.http_flow_options.keys()
                and self.http_flow_options["timeout"] != ""
            ):
                client_content = self.http_flow_options["timeout"]
                client_options = client_options + f" --timeout={client_content}"
        else:
            client_options = ""
        # Run HTTP client
        super().run(
            partial(
                run_http_client,
                self.ns_id,
                self.destination_address.get_addr(with_subnet=False),
                self.port,
                self.num_conns,
                self.rate,
                client_options,
            ),
            error_string_prefix="Running httperf",
        )

    # pylint: disable=too-many-statements
    def parse(self):
        """
        Parse HTTP output and error from self.out and self.err
        """
        # Rewind to start of the out file and read output
        self.out.seek(0)
        raw_stats_out = self.out.read().decode()

        # Rewind to start of the err file and read errors
        self.err.seek(0)
        raw_stats_err = self.err.read().decode()

        output_pattern = {}
        output_value = {}

        # pattern matching of httperf raw_stats using regex

        output_pattern["total_connections"] = r"connections (?P<totalConnections>\d+)"
        output_value["total_connections"] = re.search(
            output_pattern["total_connections"], raw_stats_out
        ).group("totalConnections")

        output_pattern["requests"] = r"requests (?P<requests>\d+)"
        output_value["request"] = re.search(
            output_pattern["requests"], raw_stats_out
        ).group("requests")

        output_pattern["replies"] = r"replies (?P<replies>\d+)"
        output_value["replies"] = re.search(
            output_pattern["replies"], raw_stats_out
        ).group("replies")

        output_pattern["test_duration[s]"] = r"test-duration (?P<testDuration>\d+.\d*)"
        output_value["test_duration[s]"] = re.search(
            output_pattern["test_duration[s]"], raw_stats_out
        ).group("testDuration")

        output_pattern[
            "connection_rate"
        ] = r"Connection rate: (?P<connectionRate>\d+.\d*)"
        output_value["connection_rate"] = re.search(
            output_pattern["connection_rate"], raw_stats_out
        ).group("connectionRate")

        output_pattern[
            "min_connection_time"
        ] = r"Connection time \[ms\]: min (?P<minConnectionTime>\d+.\d*)"
        output_value["min_connection_time"] = re.search(
            output_pattern["min_connection_time"], raw_stats_out
        ).group("minConnectionTime")

        output_pattern[
            "avg_connection_time"
        ] = r"Connection time \[ms\]: min \d+.\d* avg (?P<avgConnectionTime>\d+.\d*)"
        output_value["avg_connection_time"] = re.search(
            output_pattern["avg_connection_time"], raw_stats_out
        ).group("avgConnectionTime")

        output_pattern[
            "max_connection_time"
        ] = r"Connection time \[ms\]: min \d+.\d* avg \d+.\d* max (?P<maxConnectionTime>\d+.\d*)"
        output_value["max_connection_time"] = re.search(
            output_pattern["max_connection_time"], raw_stats_out
        ).group("maxConnectionTime")

        output_pattern[
            "median_connection_time"
            # pylint: disable=line-too-long
        ] = r"Connection time \[ms\]: min \d+.\d* avg \d+.\d* max \d+.\d* median (?P<medianConnectionTime>\d+.\d*)"
        output_value["median_connection_time"] = re.search(
            output_pattern["median_connection_time"], raw_stats_out
        ).group("medianConnectionTime")

        output_pattern[
            "stddev_connection_time"
            # pylint: disable=line-too-long
        ] = r"Connection time \[ms\]: min \d+.\d* avg \d+.\d* max \d+.\d* median \d+.\d* stddev (?P<stddevConnectionTime>\d+.\d*)"
        output_value["stddev_connection_time"] = re.search(
            output_pattern["stddev_connection_time"], raw_stats_out
        ).group("stddevConnectionTime")

        output_pattern[
            "connection_length"
        ] = r"Connection length \[replies/conn\]: (?P<connectionLength>\d+.\d*)"
        output_value["connection_length"] = re.search(
            output_pattern["connection_length"], raw_stats_out
        ).group("connectionLength")

        output_pattern["request_rate"] = r"Request rate: (?P<requestRate>\d+.\d*)"
        output_value["request_rate"] = re.search(
            output_pattern["request_rate"], raw_stats_out
        ).group("requestRate")

        output_pattern["request_size"] = r"Request size \[B\]: (?P<requestSize>\d+.\d*)"
        output_value["request_size"] = re.search(
            output_pattern["request_size"], raw_stats_out
        ).group("requestSize")

        output_pattern[
            "min_reply_rate"
        ] = r"Reply rate \[replies/s\]: min (?P<minReplyRate>\d+.\d*)"
        output_value["min_reply_rate"] = re.search(
            output_pattern["min_reply_rate"], raw_stats_out
        ).group("minReplyRate")

        output_pattern[
            "avg_reply_rate"
        ] = r"Reply rate \[replies/s\]: min \d+.\d+ avg (?P<avgReplyRate>\d+.\d*)"
        output_value["avg_reply_rate"] = re.search(
            output_pattern["avg_reply_rate"], raw_stats_out
        ).group("avgReplyRate")

        output_pattern["max_reply_rate"] = (
            r"Reply rate \[replies/s\]: "
            r"min \d+.\d+ avg \d+.\d+ "
            r"max (?P<maxReplyRate>\d+.\d*)"
        )
        output_value["max_reply_rate"] = re.search(
            output_pattern["max_reply_rate"], raw_stats_out
        ).group("maxReplyRate")

        output_pattern["stddev_reply_rate"] = (
            r"Reply rate \[replies/s\]: "
            r"min \d+.\d+ avg \d+.\d+ "
            r"max \d+.\d* stddev (?P<stddevReplyRate>\d+.\d*)"
        )
        output_value["stddev_reply_rate"] = re.search(
            output_pattern["stddev_reply_rate"], raw_stats_out
        ).group("stddevReplyRate")

        output_pattern[
            "response_reply_time"
        ] = r"response (?P<responseReplyTime>\d+.\d*)"
        output_value["response_reply_time"] = re.search(
            output_pattern["response_reply_time"], raw_stats_out
        ).group("responseReplyTime")

        output_pattern[
            "transfer_reply_time"
        ] = r"transfer (?P<transferReplyTime>\d+.\d*)"
        output_value["transfer_reply_time"] = re.search(
            output_pattern["transfer_reply_time"], raw_stats_out
        ).group("transferReplyTime")

        output_pattern["header_reply_size"] = r"header (?P<headerReplySize>\d+.\d*)"
        output_value["header_reply_size"] = re.search(
            output_pattern["header_reply_size"], raw_stats_out
        ).group("headerReplySize")

        output_pattern["content_reply_size"] = r"content (?P<contentReplySize>\d+.\d*)"
        output_value["content_reply_size"] = re.search(
            output_pattern["content_reply_size"], raw_stats_out
        ).group("contentReplySize")

        output_pattern["footer_reply_size"] = r"footer (?P<footerReplySize>\d+.\d*)"
        output_value["footer_reply_size"] = re.search(
            output_pattern["footer_reply_size"], raw_stats_out
        ).group("footerReplySize")

        output_pattern["1xx_reply_status"] = r"1xx=(?P<replyStatus1xx>\d+)"
        output_value["1xx_reply_status"] = re.search(
            output_pattern["1xx_reply_status"], raw_stats_out
        ).group("replyStatus1xx")

        output_pattern["2xx_reply_status"] = r"2xx=(?P<replyStatus2xx>\d+)"
        output_value["2xx_reply_status"] = re.search(
            output_pattern["2xx_reply_status"], raw_stats_out
        ).group("replyStatus2xx")

        output_pattern["3xx_reply_status"] = r"3xx=(?P<replyStatus3xx>\d+)"
        output_value["3xx_reply_status"] = re.search(
            output_pattern["3xx_reply_status"], raw_stats_out
        ).group("replyStatus3xx")

        output_pattern["4xx_reply_status"] = r"4xx=(?P<replyStatus4xx>\d+)"
        output_value["4xx_reply_status"] = re.search(
            output_pattern["4xx_reply_status"], raw_stats_out
        ).group("replyStatus4xx")

        output_pattern["5xx_reply_status"] = r"5xx=(?P<replyStatus5xx>\d+)"
        output_value["5xx_reply_status"] = re.search(
            output_pattern["5xx_reply_status"], raw_stats_out
        ).group("replyStatus5xx")

        output_pattern["user_cpu_time"] = r"user (?P<userCpuTime>\d+.\d*)"
        output_value["user_cpu_time"] = re.search(
            output_pattern["user_cpu_time"], raw_stats_out
        ).group("userCpuTime")

        output_pattern["system_cpu_time"] = r"system (?P<systemCpuTime>\d+.\d*)"
        output_value["system_cpu_time"] = re.search(
            output_pattern["system_cpu_time"], raw_stats_out
        ).group("systemCpuTime")

        output_pattern["net_io"] = r"Net I/O: (?P<netIO>\d+.\d*)"
        output_value["net_io"] = re.search(
            output_pattern["net_io"], raw_stats_out
        ).group("netIO")

        output_pattern["total_errors"] = r"Errors: total (?P<totalErrors>\d+)"
        output_value["total_errors"] = re.search(
            output_pattern["total_errors"], raw_stats_out
        ).group("totalErrors")

        output_pattern["client_timeout"] = r"client-timo (?P<clientTimeout>\d+)"
        output_value["client_timeout"] = re.search(
            output_pattern["client_timeout"], raw_stats_out
        ).group("clientTimeout")

        output_pattern["socket_timeout"] = r"socket-timo (?P<socketTimeout>\d+)"
        output_value["socket_timeout"] = re.search(
            output_pattern["socket_timeout"], raw_stats_out
        ).group("socketTimeout")

        output_pattern["connrefused"] = r"connrefused (?P<connectionRefused>\d+)"
        output_value["connrefused"] = re.search(
            output_pattern["connrefused"], raw_stats_out
        ).group("connectionRefused")

        output_pattern["connreset"] = r"connreset (?P<connectionReset>\d+)"
        output_value["connreset"] = re.search(
            output_pattern["connreset"], raw_stats_out
        ).group("connectionReset")

        output_pattern["other_errors"] = r"other (?P<otherErrors>\d+)"
        output_value["other_errors"] = re.search(
            output_pattern["other_errors"], raw_stats_out
        ).group("otherErrors")

        output_pattern["fd_unavail_errors"] = r"fd-unavail (?P<fdUnavailErrors>\d+)"
        output_value["fd_unavail_errors"] = re.search(
            output_pattern["fd_unavail_errors"], raw_stats_out
        ).group("fdUnavailErrors")

        output_pattern[
            "addr_unavail_errors"
        ] = r"addrunavail (?P<addrUnavailErrors>\d+)"
        output_value["addr_unavail_errors"] = re.search(
            output_pattern["addr_unavail_errors"], raw_stats_out
        ).group("addrUnavailErrors")

        output_pattern["ftab_full_errors"] = r"ftab-full (?P<ftabFullErrors>\d+)"
        output_value["ftab_full_errors"] = re.search(
            output_pattern["ftab_full_errors"], raw_stats_out
        ).group("ftabFullErrors")

        # create a stats_list which containes all the parses statistics in an ordered manner
        stats_list = []

        stats_list.append(
            {
                "total": {
                    "connections": output_value["total_connections"],
                    "requests": output_value["request"],
                    "replies": output_value["replies"],
                    "test_duration [s]": output_value["test_duration[s]"],
                },
                "connection": {
                    "connection_rate": output_value["connection_rate"],
                    "connection_time [ms]": {
                        "min": output_value["min_connection_time"],
                        "avg": output_value["avg_connection_time"],
                        "max": output_value["max_connection_time"],
                        "median": output_value["median_connection_time"],
                        "stddev": output_value["stddev_connection_time"],
                    },
                    "connection_lengh [replies/conn]": output_value[
                        "connection_length"
                    ],
                },
                "request_rate": output_value["request_rate"],
                "request_size": output_value["request_size"],
                "reply": {
                    "reply_rate": {
                        "min": output_value["min_reply_rate"],
                        "avg": output_value["avg_reply_rate"],
                        "max": output_value["max_reply_rate"],
                        "stddev": output_value["stddev_reply_rate"],
                    },
                    "reply_time [ms]": {
                        "response": output_value["response_reply_time"],
                        "transfer": output_value["transfer_reply_time"],
                    },
                    "reply_size [B]": {
                        "header": output_value["header_reply_size"],
                        "content": output_value["content_reply_size"],
                        "footer": output_value["footer_reply_size"],
                    },
                    "reply_status": {
                        "1xx": output_value["1xx_reply_status"],
                        "2xx": output_value["2xx_reply_status"],
                        "3xx": output_value["3xx_reply_status"],
                        "4xx": output_value["4xx_reply_status"],
                        "5xx": output_value["5xx_reply_status"],
                    },
                },
                "CPU Time [s]": {
                    "user": output_value["user_cpu_time"],
                    "system": output_value["system_cpu_time"],
                },
                "Net I/O [KB/s]": output_value["net_io"],
                "Errors": {
                    "total": output_value["total_errors"],
                    "client timeout": output_value["client_timeout"],
                    "socket timeout": output_value["socket_timeout"],
                    "connection refused": output_value["connrefused"],
                    "connection reset": output_value["connreset"],
                    "fd unavailable": output_value["fd_unavail_errors"],
                    "addr unavailable": output_value["addr_unavail_errors"],
                    "ftab full": output_value["ftab_full_errors"],
                    "other": output_value["other_errors"],
                },
            }
        )

        # Get Destination IP address and add results to runner
        destination_ip = self.destination_address.get_addr(with_subnet=False)
        HTTPResults.add_result(
            self.ns_id, {destination_ip: {"output": stats_list, "error": raw_stats_err}}
        )
