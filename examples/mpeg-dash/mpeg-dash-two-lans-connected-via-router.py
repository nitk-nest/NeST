# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
import os
from pathlib import Path
import sys
from nest.topology import *
from nest.experiment import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper
from nest.mpeg_dash_encoder import MpegDashEncoder
from nest import config

# IMPORTANT: It is strongly recommended that you run MPEG-DASH examples on systems
# with Ubuntu version `22.04 or above`. MPEG-DASH examples are incompatible
# with the NeST Docker image because the image uses Ubuntu Version 20.04.

# This program emulates two Local Area Networks (LANs) connected via a router.
# LAN-1 consists three hosts `h1` to `h3` connected to switch `s1`, and
# LAN-2 consists three hosts `h4` to `h6` connected to switch `s2`. Switches
# `s1` and `s2` are connected to each other via a router `r1`.
# MPEG-DASH applications have been configured between the following client,server
# pairs: (`h1`,`h4`) , (`h6`,`h2`)

##################################################################
#                       Network Topology                         #
#           LAN-1                           LAN-2                #
#   h1 ---------------                      --------------- h4   #
#                     \                    /                     #
#   h2 --------------- s1 ----- r1 ----- s2 --------------- h5   #
#                     /                    \                     #
#   h3 ---------------                      --------------- h6   #
#   <- 100mbit, 1ms ->  <- 10mbit, 10ms ->  <- 100mbit, 1ms ->   #
#                                                                #
##################################################################

# The following lines enable NeST to accept video input from a file `video.mp4`.
# This video file has to be placed in the same directory as this program.
# The encoded chunks will be generated and dumped in a folder named
# `mpeg-dash-encoded-chunks` in the same directory as this program.
CURRENT_DIR = Path(os.path.abspath(__file__)).parent
VIDEO_PATH = CURRENT_DIR / "video.mp4"
OUTPUT_PATH = CURRENT_DIR / "mpeg-dash-encoded-chunks"

# Encoding the video into MPEG-DASH chunks
mpeg_dash_encoder = MpegDashEncoder()
ENCODER_RESPONSE = mpeg_dash_encoder.encode_video(
    VIDEO_PATH, OUTPUT_PATH, overwrite=False
)
if ENCODER_RESPONSE != 0:
    sys.exit(0)

# The following line ensures that NeST does not delete encoded video chunks
# during the termination of this experiment.
config.set_value("mpeg_dash_delete_encoded_chunks_on_termination", False)

# Create six hosts 'h1' to 'h6'
h1 = Node("h1")
h2 = Node("h2")
h3 = Node("h3")
h4 = Node("h4")
h5 = Node("h5")
h6 = Node("h6")

# Create two switches 's1' and 's2'
s1 = Switch("s1")
s2 = Switch("s2")

# Create a router 'r1'
r1 = Router("r1")

# Create two networks
n1 = Network("192.168.1.0/24")  # network on the left of `r1`
n2 = Network("192.168.2.0/24")  # network on the right of `r1`

# Create LAN-1: Connect hosts `h1`, `h2` and `h3` to switch `s1`
(eth1, ets1a) = connect(h1, s1, network=n1)
(eth2, ets1b) = connect(h2, s1, network=n1)
(eth3, ets1c) = connect(h3, s1, network=n1)

# Create LAN-2: Connect hosts `h4`, `h5` and `h6` to switch `s2`
(eth4, ets2a) = connect(h4, s2, network=n2)
(eth5, ets2b) = connect(h5, s2, network=n2)
(eth6, ets2c) = connect(h6, s2, network=n2)

# Connect switches `s1` and `s2` to router `r1`
(ets1d, etr1a) = connect(s1, r1, network=n1)
(ets2d, etr1b) = connect(s2, r1, network=n2)

# Assign IPv4 addresses to all the interfaces and switches in the network.
AddressHelper.assign_addresses()

# Set the attributes of the links between hosts and switches
eth1.set_attributes("100mbit", "1ms")
eth2.set_attributes("100mbit", "1ms")
eth3.set_attributes("100mbit", "1ms")
eth4.set_attributes("100mbit", "1ms")
eth5.set_attributes("100mbit", "1ms")
eth6.set_attributes("100mbit", "1ms")

# Set the attributes of the links between `r1` and switches
etr1a.set_attributes("10mbit", "10ms")
etr1b.set_attributes("10mbit", "10ms")

# Set the packet error rates on the links.
etr1a.set_packet_corruption("0.5%", "0.1%")
etr1b.set_packet_corruption("0.5%", "0.1%")

# Set the random packet loss rate on the links.
etr1a.set_packet_loss("0.2%")
etr1b.set_packet_loss("0.2%")

# Set the default routes for hosts `h1`, `h2` and `h3` via `etr1a`
h1.add_route("DEFAULT", eth1, etr1a.address)
h2.add_route("DEFAULT", eth2, etr1a.address)
h3.add_route("DEFAULT", eth3, etr1a.address)

# Set the default routes for hosts `h4`, `h5` and `h6` via `etr1b`
h4.add_route("DEFAULT", eth4, etr1b.address)
h5.add_route("DEFAULT", eth5, etr1b.address)
h6.add_route("DEFAULT", eth6, etr1b.address)

exp = Experiment("mpeg-dash-two-lans-connected-via-router")

# In case you use GPAC MP4 Client for playback then NeST will
# generate plots of the video streaming statistics and also
# generate a JSON file of the same.
# To set the media player as GPAC MP4 Client in this example,
# set the `player` argument of `MpegDashApplication` to 'gpac'.

# In case you use VLC Media Player, then NeST won't generate video
# streaming statistics. In order to view video statistics, while
# the video is playing you will have to navigate to `Tools >
# Media Information > 'Statistics' Tab` (or use keyboard shortcut
# `CTRL+I`).
# To set the media player as VLC Media Player in this example,
# set the `player` argument of `MpegDashApplication` to 'vlc'.

# Create an MPEG-DASH application `app1` with a client node `h1` and a server node `h4`
# using their respective network interfaces (`eth1` and `eth4`). The server is
# listening on port 9000. The path specified by `OUTPUT_PATH` contains the encoded
# video chunks. The experiment duration is set to 100 seconds (It is recommended
# to set the experiment duration less or equal to the video duration).
# The media player to be used is set to 'gpac'.
app1 = MpegDashApplication(
    h1,
    h4,
    eth1.get_address(),
    eth4.get_address(),
    9000,
    OUTPUT_PATH,
    100,
    player="gpac",
)

# Create an MPEG-DASH application `app2` with a client node `h6` and a server node `h2`
# using their respective network interfaces (`eth6` and `eth2`). The server is
# listening on port 8888. The path specified by `OUTPUT_PATH` contains the encoded
# video chunks. The experiment duration is set to 100 seconds (It is recommended
# to set the experiment duration less or equal to the video duration).
# The media player to be used is set to 'gpac'.
app2 = MpegDashApplication(
    h6,
    h2,
    eth6.get_address(),
    eth2.get_address(),
    8888,
    OUTPUT_PATH,
    100,
    player="gpac",
)


exp.add_mpeg_dash_application([app1, app2])
exp.run()
