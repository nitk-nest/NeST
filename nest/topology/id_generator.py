# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

class ID_GEN:
    """
    Generate unique id
    """

    topology_id = ""
    counter = 0

    # If true, then ID_GEN.get_id will give back
    # unique id
    # Else, it will return back the original name
    # is was invoked with
    is_unique_id = True

    def __init__(self, topology_id):
        """
        Constructor to initialize the topology id
        for the class

        :param topology_id: The id used to initilize topology_id
        :type topology_id: string
        """
        ID_GEN.topology_id = topology_id

    @staticmethod
    def get_id(name):
        """
        NOTE: Update doc
        Geneartes unique id on each call
        """
        if ID_GEN.is_unique_id:
            ID_GEN.counter += 1
            return ID_GEN.topology_id+"-"+str(ID_GEN.counter)
        else:
            return name

    @staticmethod
    def enable_unique_id():
        """
        If disabled, enable generation of 
        unique id
        """

        ID_GEN.is_unique_id = True

    @staticmethod
    def disable_unique_id():
        """
        If enabled, disable generation of unique id
        """

        ID_GEN.is_unique_id = False
