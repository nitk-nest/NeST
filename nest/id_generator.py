# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

class ID_GEN:
    """
    Generate unique id
    """

    topology_id = ""
    counter = 0

    def __init__(self, topology_id):
        """
        Constructor to initialize the topology id
        for the class

        :param topology_id: The id used to initilize topology_id
        :type topology_id: string
        """
        ID_GEN.topology_id = topology_id

    @staticmethod
    def get_id():
        """
        Geneartes unique id on each call
        """
        ID_GEN.counter += 1
        return ID_GEN.topology_id+"-"+str(ID_GEN.counter)