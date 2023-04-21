# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2024 NITK Surathkal

"""User API to setup and run experiments on a given topology"""

import copy
import logging
from collections import defaultdict
from pathlib import Path
import random
import sys
from nest import engine, config
from nest.input_validator.metric import Bandwidth
from nest.network_utilities import ipv6_dad_check
from nest.input_validator import input_validator
from nest.topology import Node, Address
from nest.topology.interface import BaseInterface
from nest.topology_map import TopologyMap
from .run_exp import run_experiment
from .pack import Pack
from .tools import Iperf3Options
from .helpers.tcp_validations import TCPValidations

logger = logging.getLogger(__name__)
tcp_validator = TCPValidations()


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
class Flow:
    """Defines a flow in the topology"""

    # pylint: disable=too-many-arguments
    @input_validator
    def __init__(
        self,
        source_node: Node,
        destination_node: Node,
        destination_address: Address,
        start_time: int,
        stop_time: int,
        number_of_streams: int,
        source_address: Address = None,
    ):
        """
        'Flow' object in the topology

        Parameters
        ----------
        source_node : Node
            Source node of flow
        destination_node : Node
            Destination node of flow
        destination_address : Address/str
            Destination address of flow
        start_time : int
            Time to start flow (in seconds)
        stop_time : int
            Time to stop flow (in seconds)
        number_of_streams : int
            Number of streams in the flow
        source_address : Address/str
            Source address of flow
        """
        self.source_node = source_node
        self.destination_node = destination_node
        self.destination_address = destination_address
        self.start_time = start_time
        self.stop_time = stop_time
        self.number_of_streams = number_of_streams
        if source_address is None:
            self.source_address = source_node.interfaces[0].get_address()
        else:
            self.source_address = source_address

        self._options = {"protocol": "TCP", "cong_algo": "cubic"}
        self.user_input_options = {}

    @property
    def source_address(self):
        """Getter for source address"""
        return self._source_address

    @source_address.setter
    def source_address(self, source_address):
        """Setter for source address"""
        if isinstance(source_address, str):
            source_address = Address(source_address)
        self._source_address = source_address

    @property
    def destination_address(self):
        """Getter for destination address"""
        return self._destination_address

    @destination_address.setter
    def destination_address(self, destination_address):
        """Setter for destination address"""
        if isinstance(destination_address, str):
            destination_address = Address(destination_address)
        self._destination_address = destination_address

    def _get_props(self):
        """
        Get flow properties.

        NOTE: To be used internally
        """

        return [
            self.source_node.id,
            self.destination_node.id,
            self.destination_address.get_addr(with_subnet=False),
            self.start_time,
            self.stop_time,
            self.number_of_streams,
            self._options,
            self.source_address.get_addr(with_subnet=False),
        ]

    def __repr__(self):
        classname = self.__class__.__name__
        return (
            f"{classname}({self.source_node!r}, {self.destination_node!r}, {self.source_address!r},"
            f" {self.destination_address!r}), {self.start_time!r}, {self.stop_time!r}"
            f" {self.number_of_streams!r})"
        )

    @property
    def protocol(self):
        """Getter for protocol"""
        return self._options["protocol"]

    @staticmethod
    @input_validator
    # pylint: disable=too-many-arguments
    def setup_mptcp_connection(
        source_interface: BaseInterface,
        destination_interface: BaseInterface,
        start_time: int,
        stop_time: int,
        number_of_streams: int = 1,
    ):
        """
        Creates and returns an MPTCP flow for given source and destination
        interface with all MPTCP endpoints enabled on both nodes

        Parameters
        ----------
        source_interface : Interface
            Source interface for MPTCP Flow
        destination_interface : Interface
            Destination interface for MPTCP Flow
        start_time : int
            Start time for the flow
        stop_time : int
            Stop time for the flow
        number_of_streams : int = 1
            Number of streams in the flow

        Returns
        -------
        Flow
            An MPTCP capable flow from source_interface to destination_interface
        """

        # Enable MPTCP on the Source Nodes
        source_node = TopologyMap.get_node(source_interface.node_id)
        source_node.enable_mptcp()

        # Enable MPTCP on the Destination Node
        destination_node = TopologyMap.get_node(destination_interface.node_id)
        destination_node.enable_mptcp()

        # Set MPTCP limits on both the nodes
        add_addr_limit = min(
            5, max(len(source_node.interfaces), len(destination_node.interfaces))
        )
        max_subflow_limit = min(
            5, len(source_node.interfaces) * len(destination_node.interfaces) - 1
        )
        source_node.set_mptcp_parameters(
            max_subflows=max_subflow_limit, max_add_addr_accepted=add_addr_limit
        )
        destination_node.set_mptcp_parameters(
            max_subflows=max_subflow_limit, max_add_addr_accepted=add_addr_limit
        )

        # Check if MPTCP can be run between the 2 hosts as per RFC
        if not (
            source_node.is_mptcp_supported() or destination_node.is_mptcp_supported()
        ):
            logger.error(
                "Neither of your source node and destination node is multihomed and "
                "multiadressed. Please check your topology and try again."
            )
            sys.exit()

        # If MPTCP can be run, enable all interfaces as MPTCP endpoints with default flags
        for interface in source_node.interfaces:
            interface.enable_mptcp_endpoint(
                ["subflow", "fullmesh"]
                if "fullmesh" in engine.possible_mptcp_flags
                else ["subflow"]
            )
        for interface in destination_node.interfaces:
            interface.enable_mptcp_endpoint(["signal"])

        # Create and return a flow that will work with MPTCP
        return Flow(
            source_node,
            destination_node,
            destination_interface.get_address(),
            start_time,
            stop_time,
            number_of_streams,
            source_address=source_interface.get_address(),
        )


class Application:
    """Defines an application in the topology"""

    @input_validator
    def __init__(
        self,
        source_node: Node,
        destination_node: Node,
        destination_address: Address,
    ):
        """
        'Application' object in the topology

        Parameters
        ----------
        source_node : Node
            Source node of application
        destination_node : Node
            Destination node of application
        destination_address : Address/str
            Destination address of application
        """
        self.source_node = source_node
        self.destination_node = destination_node
        self.destination_address = destination_address

    @property
    def destination_address(self):
        """Getter for destination address"""
        return self._destination_address

    @destination_address.setter
    def destination_address(self, destination_address):
        """Setter for destination address"""
        if isinstance(destination_address, str):
            destination_address = Address(destination_address)
        self._destination_address = destination_address

    def _get_props(self):
        """
        Get application properties.

        NOTE: To be used internally
        """

        return [
            self.source_node.id,
            self.destination_node.id,
            self.destination_address.get_addr(with_subnet=False),
        ]

    def __repr__(self):
        classname = self.__class__.__name__
        return (
            f"{classname}({self.source_node!r}, {self.destination_node!r},"
            f" {self.destination_address!r})"
        )


class CoapApplication(Application):
    """Defines a CoAP application in the topology"""

    # pylint: disable=too-many-arguments
    @input_validator
    def __init__(
        self,
        source_node: Node,
        destination_node: Node,
        destination_address: Address,
        n_con_msgs: int,
        n_non_msgs: int,
        user_options=None,
    ):
        """
        Application object representing CoAP applications in the topology.
        Inherited from the `Application` class.
        Application object representing CoAP applications in the topology.
        Inherited from the `Application` class.

        Parameters
        ----------
        source_node : Node
            Source node of flow
        destination_node : Node
            Destination node of flow
        destination_address : Address/str
            Destination address of flow
        n_con_msgs : int
            Number of confimable messages to be sent in the flow
        n_non_msgs : int
            Number of non-confimable messages to be sent in the flow
        user_options : dict, optional
            User specified options for particular tools
        """
        self.n_con_msgs = n_con_msgs
        self.n_non_msgs = n_non_msgs

        # Options for users to set
        self.user_options = user_options
        super().__init__(source_node, destination_node, destination_address)
        super().__init__(source_node, destination_node, destination_address)

    # Destination address getter and setter are implemented
    # in the Application class which is the superclass of CoapApplication class
    # in the Application class which is the superclass of CoapApplication class

    def _get_props(self):
        """
        Get flow properties.

        NOTE: To be used internally
        """

        return [
            self.source_node.id,
            self.destination_node.id,
            self.destination_address.get_addr(with_subnet=False),
            self.n_con_msgs,
            self.n_non_msgs,
            self.user_options,
        ]

    def __repr__(self):
        classname = self.__class__.__name__
        return (
            f"{classname}({self.source_node!r}, {self.destination_node!r},"
            f" {self.destination_address!r}),"
            f" {self.n_con_msgs!r}, {self.n_non_msgs!r}, {self.user_options!r})"
        )


class MpegDashApplication(Application):
    """Defines an MPEG DASH application in the topology"""

    supported_media_players = ["gpac", "vlc"]

    # pylint: disable=too-many-arguments
    @input_validator
    def __init__(
        self,
        source_node: Node,
        destination_node: Node,
        source_address: Address,
        destination_address: Address,
        port: int,
        encoded_chunks_path: Path,
        duration: int,
        player: str,
        additional_player_options=None,
    ):
        """
        Application object representing MPEG-DASH applications in the topology.
        Inherited from the `Application` class.

        Parameters
        ----------
        source_node : Node
            Node that behaves as MPEG-DASH client
        destination_node : Node
            Node that behaves as MPEG-DASH server
        source_address : Address/str
            Address of the MPEG-DASH client
        destination_address : Address/str
            Address of the MPEG-DASH server
        port : int
            Port number of the server at which MPEG-DASH application is running
        encoded_chunks_path : Path
            The path where the encoded chunks are stored.
        duration : int
            Number of seconds for which experiment has to be run
        player: str
            The media player to be used.
        additional_player_options : list, optional
            User specified options for the video player
        """
        self.source_address = source_address
        self.port = port
        self.encoded_chunks_path = encoded_chunks_path
        self.duration = duration
        self.player = player
        self.additional_player_options = additional_player_options

        super().__init__(source_node, destination_node, destination_address)

        if self.player not in self.supported_media_players:
            raise RuntimeError(
                f"Invalid media player {self.player}!",
                "NeST currently supports the following media players:",
                f"{self.supported_media_players}.",
                "Please specify one of these.",
            )

        if self.additional_player_options is not None:
            self.additional_player_options = " ".join(self.additional_player_options)
        else:
            self.additional_player_options = ""

    def _get_props(self):
        """
        Get flow properties.

        NOTE: To be used internally
        """
        return [
            self.source_node.id,
            self.destination_node.id,
            self.source_address.get_addr(with_subnet=False),
            self.destination_address.get_addr(with_subnet=False),
            self.port,
            self.encoded_chunks_path,
            self.duration,
            self.player,
            self.additional_player_options,
        ]

    def __repr__(self):
        classname = self.__class__.__name__
        return (
            f"{classname}({self.source_node!r}, {self.destination_node!r},"
            f" {self.source_address!r}, {self.destination_address!r}, {self.port!r},"
            f" {self.encoded_chunks_path!r}, {self.duration!r},"
            f" {self.player!r}, {self.additional_player_options!r})"
        )


class Experiment:
    """Handles experiment to be run on topology"""

    # Stores configuration of old and new congestion algorithms for cleanup
    old_cong_algos = defaultdict(dict)
    new_cong_algos = []

    @input_validator
    def __init__(self, name: str):
        """
        Create experiment

        Parameters
        ----------
        name : str
            Name of experiment
        """
        self.name = name
        self.flows = []
        self.coap_applications = []
        self.mpeg_dash_applications = []
        self.node_stats = []
        self.qdisc_stats = []
        self.tcp_module_params = defaultdict(dict)

    def add_flow(self, flow):
        """
        Add flow to experiment
        By default, the flow is assumed to be
        TCP with cubic congestion algorithm

        Parameters
        ----------
        flow : Flow
            Add flow to experiment
        """
        self.flows.append(copy.deepcopy(flow))

    @input_validator
    def add_tcp_flow(
        self,
        flow: Flow,
        congestion_algorithm="cubic",
        tool: str = "netperf",
        **kwargs: dict,
    ):
        """
        Add TCP flow to experiment. If no congestion control algorithm
        is specified, then by default cubic is used.

        Note: The congestion control algorithm specified in this API
        overrides the congestion control algorithm specified in
        `topology.Node.configure_tcp_param()` API.

        Parameters
        ----------
        flow : Flow
            Flow to be added to experiment
        congestion_algorithm : str
            TCP congestion algorithm (Default value = 'cubic')
        tool : str
            Tool (netperf/iperf3) to be used for the experiment (Default value = 'netperf')
        """

        tcp_validator.verify_tool(tool)
        tcp_validator.verify_congestion_control_algorithm(congestion_algorithm)

        # TODO: Verify congestion algorithm

        options = {
            "protocol": "TCP",
            "cong_algo": congestion_algorithm,
            "tool": tool,
        }

        if tool == "iperf3":
            user_options = {}

            for params, value in kwargs.items():
                if params == "server_options":
                    user_options.update(value)

                if params == "client_options":
                    user_options.update(value)

            iperf3options = Iperf3Options(kwargs=user_options).getter()
            if (
                "port_nos" not in iperf3options
                or len(iperf3options["port_nos"]) < flow.number_of_streams
            ):
                port_nos = set()
                # If user has provided certain port_nos, use them
                if iperf3options.get("port_nos") is not None:
                    port_nos = set(iperf3options["port_nos"])
                while len(port_nos) < flow.number_of_streams:
                    port_nos.add(random.randrange(1024, 65536))
                iperf3options.update({"port_nos": list(port_nos)})

            # iperf3options.update(options)
            options = {**iperf3options, **options}

        flow._options = options  # pylint: disable=protected-access
        self.add_flow(flow)

    @input_validator
    def add_mptcp_flow(
        self,
        flow: Flow,
        congestion_algorithm="cubic",
        tool: str = "netperf",
        **kwargs: dict,
    ):
        """
        Add MPTCP flow to experiment. If no congestion control algorithm
        is specified, then by default cubic is used.

        Note: The congestion control algorithm specified in this API
        overrides the congestion control algorithm specified in
        `topology.Node.configure_tcp_param()` API.

        Parameters
        ----------
        flow : Flow
            Flow to be added to experiment
        congestion_algorithm : str
            TCP congestion algorithm (Default value = 'cubic')
        tool : str
            Tool (netperf/iperf3) to be used for the experiment
            (Default value = 'netperf')
        """
        tcp_validator.verify_tool(tool)
        tcp_validator.verify_congestion_control_algorithm(congestion_algorithm)

        options = {
            "protocol": "MPTCP",
            "cong_algo": congestion_algorithm,
            "tool": tool,
        }

        if tool == "iperf3":
            user_options = {}

            for params, value in kwargs.items():
                if params == "server_options":
                    user_options.update(value)

                if params == "client_options":
                    user_options.update(value)

            iperf3options = Iperf3Options(kwargs=user_options).getter()
            if (
                "port_nos" not in iperf3options
                or len(iperf3options["port_nos"]) < flow.number_of_streams
            ):
                port_nos = set()
                # If user has provided certain port_nos, use them
                if iperf3options.get("port_nos") is not None:
                    port_nos = set(iperf3options["port_nos"])
                while len(port_nos) < flow.number_of_streams:
                    port_nos.add(random.randrange(1024, 65536))
                iperf3options.update({"port_nos": list(port_nos)})

            # iperf3options.update(options)
            options = {**iperf3options, **options}

        flow._options = options  # pylint: disable=protected-access
        self.add_flow(flow)

    @input_validator
    def add_udp_flow(
        self,
        flow: Flow,
        target_bandwidth: Bandwidth = Bandwidth("1mbit"),
        server_options: dict = None,
        client_options: dict = None,
    ):
        """
        Add UDP flow to experiment

        Parameters
        ----------
        flow : Flow
            Flow to be added to experiment
        target_bandwidth :
            UDP bandwidth (in Mbits) (Default value = '1mbit')
            This bandwidth limit is for each UDP stream in the flow
        """
        options = {"protocol": "udp", "target_bw": target_bandwidth.string_value}

        # options update with user configuration
        user_options = {}
        if server_options:
            user_options.update(server_options)
        if client_options:
            user_options.update(client_options)

        iperf3options = Iperf3Options(protocol="udp", kwargs=user_options).getter()

        if "port_no" not in iperf3options:
            iperf3options.update({"port_no": random.randrange(1024, 65536)})

        iperf3options.update(options)

        # pylint: disable=protected-access
        flow._options = iperf3options
        self.add_flow(flow)

    @input_validator
    def add_coap_application(self, coap_application: CoapApplication):
        """
        Add a CoAP application to experiment

        Parameters
        ----------
        coap_application : CoapApplication
            The coap application to be added to experiment
        """
        self.coap_applications.append(copy.deepcopy(coap_application))

    @input_validator
    def add_mpeg_dash_application(self, mpeg_dash_applications):
        """
        Add an MPEG-DASH application to the experiment

        Parameters
        ----------
        mpeg_dash_applications : Union[MpegDashApplication,list]
            The MPEG-DASH application(s) to be added to experiment
        """
        if isinstance(mpeg_dash_applications, MpegDashApplication):
            self.mpeg_dash_applications.append(copy.deepcopy(mpeg_dash_applications))

        elif isinstance(mpeg_dash_applications, list):
            self.mpeg_dash_applications.extend(copy.deepcopy(mpeg_dash_applications))

        else:
            raise Exception(
                """The add_mpeg_dash_application function takes either
                a MpegDashApplication object or a list of the same only."""
            )

    @input_validator
    def require_qdisc_stats(self, interface: BaseInterface, stats=""):
        """
        Stats to be obtained from qdisc in interface

        Parameters
        ----------
        interface : BaseInterface
            Interface containing the qdisc
        stats : list(str)
            Stats required (Default value = '') [NOT SUPPORTED]
        """
        # TODO: Leads to rewrite if the function is called
        # twice with same 'interface'

        # for stat in stats:
        #     if stat not in Experiment.qdisc_stats:
        #         raise ValueError('{} is not a valid Queue property.'.format(stat))

        if interface.get_qdisc() is None:
            raise ValueError("Given interface hasn't been assigned any qdisc.")

        self.qdisc_stats.append(
            {
                "ns_id": interface.node_id,
                "int_id": interface.ifb_id,
                "qdisc": interface.get_qdisc().qdisc,
                "stats": stats,
            }
        )

    def configure_tcp_module_params(self, congestion_algorithm, **kwargs):
        """
        Set TCP module parameters

        Parameters
        ----------
        congestion_algorithm : str
            TCP congestion algorithm
        **kwargs :
            module parameters to set
        """
        self.tcp_module_params[congestion_algorithm].update(kwargs)
        logger.info("TCP module parameters will be set when the experiment is run")

    @ipv6_dad_check
    def run(self):
        """Run the experiment"""
        print()
        logger.info("Running experiment %s ", self.name)
        Pack.init(self.name)
        if config.get_value("show_mptcp_checklist"):
            tcp_validator.verify_mptcp_setup(self)
        run_experiment(self)

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}({self.name!r})"
