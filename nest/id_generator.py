# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

class ID_GEN:

    topology_id = ""
    counter = 0

    def __init__(self, topology_id):
        ID_GEN.topology_id = topology_id

    @staticmethod
    def get_id():
        ID_GEN.counter += 1
        return ID_GEN.topology_id+"-"+str(ID_GEN.counter)