# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to creation of IFB for qdiscs in topology"""

import logging
import nest.config as config
from nest import engine
from nest.topology.device import Device

logger = logging.getLogger(__name__)

# Max length of interface when Topology Map is disabled
# i.e. 'assign_random_names' is set to False in config
MAX_CUSTOM_NAME_LEN = 15

# pylint: disable=too-many-instance-attributes


class Ifb(Device):
    """
    This is the IFB created to be able to add two classless
    qdiscs, netem and another on a single interface

    Attributes
    ----------
    id : str
        This value is used by `engine` to create emulated IFB
        entity
    node_id : str
        id of the Node to  which this IFB belongs
    interface_id : str
        The id of the interface that the IFB is attached to
    bandwidth : str
        The bandwidth set to the device
    qdisc : str
        The qdisc assigned to the interface
    """

    def __init__(self, name, node_id, interface_id):
        """
        Constructor for an IFB

        Created only if bandwidth is given or default bandwidth is set
        in case of adding qdisc and delay buy bandwidth not specified

        Parameters
        ----------
        name : str
            User given name for the interface
        node_id : str
            This is the id of the node that the device belongs to
        """

        self.qdisc = None
        if config.get_value("assign_random_names") is False:
            if len(name) > MAX_CUSTOM_NAME_LEN:
                raise ValueError(
                    f"Interface name {name} is too long. Interface names "
                    f"should not exceed 15 characters"
                )

        super().__init__(name, node_id)
        self.interface_id = interface_id
        engine.create_ifb(self._id)
        self.set_mode("UP")

        self.current_bandwidth = config.get_value("default_bandwidth")
        self._set_default_bandwidth()

    def _set_default_bandwidth(self):
        """
        Sets default bandwidth to the IFB
        """

        default_route = {"default": "1"}

        # TODO: find how to set a good bandwidth
        default_bandwidth = {"rate": config.get_value("default_bandwidth")}

        # TODO: Standardize this; seems like arbitrary handle values
        # were chosen.
        # HTB class is added since, to use a filter and redirect traffic,
        # a classid is needed and htb gives it that, since it's a class
        self.add_qdisc("htb", "root", "1:", **default_route)
        self.add_class("htb", "1:", "1:1", **default_bandwidth)
        self.add_qdisc("pfifo", "1:1", "11:")

        action_redirect = {
            "match": "u32 0 0",  # from man page examples
            "action": "mirred",
            "egress": "redirect",
            "dev": self.id,
        }

        # NOTE: Use Filter API
        # Action mirred, redicting traffic, etc is needed since netem and
        # the user giver qdisc are both classless and cannot be added to
        # the same device
        engine.add_filter(
            self._node_id,
            self.interface_id,
            "all",
            "1",
            "u32",
            parent="1:",
            **action_redirect,
        )

    def set_bandwidth(self, bandwidth):
        """
        Set a maximum bandwidth for the ifb

        Paramaters
        ----------
        bandwidth : str
            The bandwidth that has to be set with the units
        """

        self.current_bandwidth = bandwidth

        bandwidth_parameter = {"rate": bandwidth}
        self.change_class("htb", "1:", "1:1", **bandwidth_parameter)

    def set_qdisc(self, qdisc, **kwargs):
        """
        Adds the Queueing algorithm to the interface

        Parameters
        ----------
        qdisc : string
            The Queueing algorithm to be added
        bandwidth :
            Link bandwidth
        """
        # TODO: Don't use this API directly. If it used,
        # then the bandwidth should be same as link bandwidth
        # (A temporary bug fix is causing this issue. Look for
        # a permanent solution)
        # TODO: Check if this is a redundant condition

        current_bandwidth_parameter = {"rate": self.current_bandwidth}

        engine.change_class(
            self._node_id, self.id, "1:", "htb", "1:1", **current_bandwidth_parameter
        )

        self.delete_qdisc("11:")
        self.add_qdisc(qdisc, "1:1", "11:", **kwargs)
