# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

"""Validation helper for TCP Flows and Experiments"""
from colorama import Fore, Style
from nest.experiment.constants.tcp_congestion_control_algorithms import (
    congestion_algo_list,
)


class TCPValidations:
    """
    Validates vaious aspects of TCP experiments
    """

    SUCCESS_LOG = Fore.GREEN + "\N{check mark}"
    FAILURE_LOG = Fore.RED + "\N{cross mark}"
    NEUTRAL_LOG = Style.RESET_ALL + "\N{bullet}"

    def __log_success(self, msg: str):
        print(self.SUCCESS_LOG, msg)

    def __log_failure(self, msg: str):
        print(self.FAILURE_LOG, msg)

    def __log_neutral(self, msg: str):
        print(self.NEUTRAL_LOG, msg)

    def verify_tool(self, tool):
        """
        Verifies the tool to be either of iperf3 or netperf

        Parameters
        ----------
        tool : string
            Tool selected for TCP experiment
        """
        if tool not in ["iperf3", "netperf"]:
            raise ValueError(
                f"{tool} is not a valid performance tool. Should be either netperf/iperf3"
            )

    def verify_congestion_control_algorithm(self, congestion_algorithm):
        """
        Verifies the congestion control algorithm to be
        one from the congestion algorithm list

        Parameters
        ----------
        congestion_algorithm : string
            Congestion control algorithm selected for the experiment
        """
        if congestion_algorithm not in congestion_algo_list:
            raise ValueError(
                f"{congestion_algorithm} is not a valid TCP Congestion Control algorithm"
            )

    # pylint: disable=too-many-branches
    def verify_mptcp_setup(self, experiment):
        """
        This function prepares a checklist that tells the user whether their
        topology is MPTCP enabled.

        Parameters
        ----------
        experiment: Experiment
            Experiment object that may contain some flows for the experiment
        """

        print(Style.BRIGHT, "\nMPTCP Logger Invoked", Style.RESET_ALL)

        # Check if there is atleast one MPTCP flow in the experiment
        if not any(map(lambda flow: flow.protocol == "MPTCP", experiment.flows)):
            self.__log_failure("No MPTCP Flows found in this experiment")
        else:
            self.__log_success("MPTCP Flows exist in this experiment")

        print(Style.RESET_ALL)

        # Loop over every flow
        for flow in filter(lambda x: x.protocol == "MPTCP", experiment.flows):
            self.__log_neutral(f"{Style.BRIGHT}{flow}{Style.RESET_ALL}")

            # Source Node must be MPTCP enabled
            if flow.source_node.is_mptcp:
                self.__log_success(
                    f"Source Node {flow.source_node.name} is MPTCP enabled"
                )
            else:
                self.__log_failure(
                    f"Source Node {flow.source_node.name} is not MPTCP enabled"
                )

            # Destination Node must be MPTCP enabled
            if flow.destination_node.is_mptcp:
                self.__log_success(
                    f"Destination Node {flow.destination_node.name} is MPTCP enabled"
                )
            else:
                self.__log_failure(
                    f"Destination Node {flow.destination_node.name} is not MPTCP enabled"
                )

            # Either the source or the destination must be multi-homed and multi-addressed
            if (
                flow.source_node.is_mptcp_supported()
                or flow.destination_node.is_mptcp_supported()
            ):
                self.__log_success(
                    f"Either of the hosts {flow.source_node.name} or {flow.destination_node.name} "
                    f"is multi-homed and multi-addressed"
                )
            else:
                self.__log_failure(
                    f"Neither of the hosts {flow.source_node.name} or {flow.destination_node.name} "
                    f"is multi-homed and multi-addressed"
                )

            # Source Node must have atleast 1 interface with
            # MPTCP enabled subflow or fullmesh endpoints
            if any(
                list(
                    map(
                        lambda interface: interface.get_mptcp_endpoints() is not None
                        and any(
                            list(
                                map(
                                    lambda y: "subflow" in y or "fullmesh" in y,
                                    interface.get_mptcp_endpoints().values(),
                                )
                            )
                        ),
                        flow.source_node.interfaces,
                    )
                )
            ):
                self.__log_success(
                    f"Atleast 1 interface on Source Node {flow.source_node.name} "
                    f"has a subflow/fullmesh MPTCP endpoint"
                )
            else:
                self.__log_neutral(
                    f"No interface on Source Node {flow.source_node.name} "
                    f"has a subflow/fullmesh MPTCP endpoint"
                )

            # Destination Node must have atleast 1 interface with
            # MPTCP enabled signal endpoint
            if any(
                list(
                    map(
                        lambda interface: interface.get_mptcp_endpoints() is not None
                        and any(
                            map(
                                lambda y: "signal" in y,
                                interface.get_mptcp_endpoints().values(),
                            )
                        ),
                        flow.destination_node.interfaces,
                    )
                )
            ):
                self.__log_success(
                    f"Atleast 1 interface on Destination Node {flow.destination_node.name} "
                    f"has a signal MPTCP endpoint"
                )
            else:
                self.__log_neutral(
                    f"No interface on Destination Node {flow.destination_node.name} "
                    f"has a signal MPTCP endpoint"
                )
            print(Style.RESET_ALL)
