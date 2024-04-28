# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

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
# with Ubuntu version `22.04 or above`.

#################################
#       Network Topology        #
#                               #
#          5mbit, 5ms -->       #
#   h1 ------------------- h2   #
#       <-- 10mbit, 100ms       #
#                               #
#################################

# In the following lines below, NeST will require a video file which will be utilised for streaming.
# The user is advised to perform any one of the following tasks:
# i. Either copy a video file in the same directory as these examples and rename it as 'video.mp4', or
# ii. Set the 'VIDEO_PATH' variable in the example to the path of the video file of the user's choice.
# If the path specified by 'VIDEO_PATH' is invalid, then the API will automatically resort to
# downloading a sample 15-second video from the Internet as a fallback mechanism. The sample video
# will be downloaded from https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4 .

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

# Create two hosts `h1` and `h2`.
h1 = Node("h1")
h2 = Node("h2")

# Set the IPv4 address for the network, and not the interfaces.
# We will use the `AddressHelper` later to assign addresses to the interfaces.
n1 = Network("192.168.1.0/24")

# Connect the above two hosts using a veth pair. Note that `connect` API in
# this program takes `network` as an additional parameter. The following line
# implies that `eth1` and `eth2` interfaces on `h1` and `h2`, respectively are
# in the same network `n1`.
(eth1, eth2) = connect(h1, h2, network=n1)

# Assign IPv4 addresses to all the interfaces in the network.
AddressHelper.assign_addresses()

# Set the link attributes: `h1` --> `h2` and `h2` --> `h1`
eth1.set_attributes("5mbit", "5ms")
eth2.set_attributes("10mbit", "100ms")

# Set a packet error rate of 0.5% with 0.1% correlation rate between two packets
# on the links from `h1` to `h2` and `h2` to `h1`.
eth1.set_packet_corruption("0.5%", "0.1%")
eth2.set_packet_corruption("0.5%", "0.1%")

# Set the random packet loss rate on the links from `h1` to `h2` and `h2` to `h1`.
eth1.set_packet_loss("0.2%")
eth2.set_packet_loss("0.2%")

exp = Experiment("mpeg-dash-point-to-point-1")

# In case you use GPAC MP4 Client for playback then NeST will
# generate plots of the video streaming statistics and also
# generate a JSON file of the same.

# In case you use VLC Media Player, then NeST won't generate video
# streaming statistics. In order to view video statistics, while
# the video is playing you will have to navigate to `Tools >
# Media Information > 'Statistics' Tab` (or use keyboard shortcut
# `CTRL+I`).

# To set the media player as GPAC MP4 Client or VLC Media Player in this example,
# set the `player` argument of `MpegDashApplication` to 'gpac' or 'vlc' respectively.

# Create an MPEG-DASH application with a client node `h1` and a server node `h2`
# using their respective network interfaces (`eth1` and `eth2`). The server is
# listening on port 8000. The path specified by `OUTPUT_PATH` contains the encoded
# video chunks. The experiment duration is set to 100 seconds (It is recommended
# to set the experiment duration less or equal to the video duration).
# The media player to be used is set to 'gpac'. The audio playback, which is disabled
# by default, can be enabled by setting `enable_audio_playback` to `True`.

app = MpegDashApplication(
    h1,
    h2,
    eth1.get_address(),
    eth2.get_address(),
    8000,
    OUTPUT_PATH,
    100,
    player="gpac",
    enable_audio_playback=False,
)

exp.add_mpeg_dash_application(app)
exp.run()
