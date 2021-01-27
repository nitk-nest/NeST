# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
import subprocess
import multiprocessing

from nest.experiment import *
from nest.topology import *

##############################
# Topology
#
# n1 ----- n2
#
##############################

# Create two nodes, connect them and assign address to their
# respctive interfaces
n1 = Node("n1")
n2 = Node("n2")

(n1_n2, n2_n1) = connect(n1, n2)

n1_n2.set_address("10.0.0.1/24")
n2_n1.set_address("10.0.0.2/24")

# Set number of ping packets sent and number of packets to be captured
# by tcpdump
PING_PACKETS_SENT = 10
MAX_PACKETS_CAPTURED = 20

# Initiate ping (for 10s) in n1 as a seperate process
print(f"Sending {PING_PACKETS_SENT} ping packets from n1 to n2...")
process = multiprocessing.Process(
    target=n1.ping, args=(n2_n1.address, PING_PACKETS_SENT, False)
)
process.start()

# Now run a packet capture in n2
with n2:
    print("Running tcpdump in n2 to capture ping packets...")
    proc = subprocess.Popen(
        ["tcpdump", "-i", n2_n1.id, f"-c {MAX_PACKETS_CAPTURED}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    (stdout, _) = proc.communicate()

# Output packet capture after ping thread finishes
process.join()
print(f"\nPackets captured at n2 by tcpdump (max: {MAX_PACKETS_CAPTURED} packets):\n")
print(stdout.decode())
