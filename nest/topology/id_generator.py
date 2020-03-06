# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

class ID_GEN:
    """
    Generate unique id
    """

    topology_id = ""
    counter = 0

    abstraction = True

    def __init__(self, topology_id, abstraction = True):
        """
        NOTE: Update doc
        Constructor to initialize the topology id
        for the class

        :param topology_id: The id used to initilize topology_id
        :type topology_id: string
        """
        ID_GEN.topology_id = topology_id
        ID_GEN.abstraction = True

    @staticmethod
    def get_id(name):
        """
        NOTE: Update doc
        Geneartes unique id on each call
        """
        if ID_GEN.abstraction:
            ID_GEN.counter += 1
            return ID_GEN.topology_id+"-"+str(ID_GEN.counter)
        else:
            return name

    @staticmethod
    def enable_abstraction():

        ID_GEN.abstraction = True

    @staticmethod
    def disable_abstraction():

        ID_GEN.abstraction = False
    