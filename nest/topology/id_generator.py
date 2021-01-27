# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Generate unique id for topology entity"""

from .. import config


class IdGen:  # pylint: disable=too-few-public-methods
    """Generate unique id for Topology entities


    Attributes
    ----------
    topology_id: str
        Id prefixed for each topology entity
    counter: int
        Unique identifier of an entity within a topology
    is_unique_id: bool
        If unique Id's should be used for entity names
        (default is True)

    """

    topology_id = ""
    counter = 0

    def __init__(self, topology_id):
        """Initialize `topology_id`

        Parameters
        ----------
        topology_id: str

        """
        IdGen.topology_id = topology_id

    @staticmethod
    def get_id(name):
        """Generate unique id on each call

        Parameters
        ----------
        name: str
            Name of the entity as shown to the user

        Returns
        -------
        str
            If `is_unique_id` is true, then an unique id is returned
            Else, `name` is returned back

        """
        if config.get_value("assign_random_names"):
            IdGen.counter += 1
            return IdGen.topology_id + "-" + str(IdGen.counter)

        return name
