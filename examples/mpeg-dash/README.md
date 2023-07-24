# Examples to demonstrate how to stream videos using MPEG DASH in NeST

This directory contains the following example to understand how videos can be streamed using MPEG DASH in `NeST`. `MpegDashApplication` API is used in these examples to configure stream video between a pair of nodes.


`IMPORTANT`
It is strongly recommended that you run these MPEG-DASH examples on systems with Ubuntu version `22.04 or above`. These MPEG-DASH examples are incompatible with the NeST Docker image because the image uses Ubuntu Version 20.04.
All the examples listed below require `vlc` and `gpac` to be pre-installed in your machine.
The installation command is as follows:

```shell
sudo apt install vlc gpac
```

Ensure that the installed `gpac` version is `2.0 or above`.

In case you use GPAC MP4 Client for playback then NeST will generate plots of the video streaming statistics and also generate a JSON file of the same.
To set media player as GPAC MP4 Client in the below examples, set the `player` argument of `MpegDashApplication` to 'gpac'.

In case you use VLC Media Player, then while the video is playing you will have to navigate to `Tools > Media Information > 'Statistics' Tab` (or use keyboard shortcut `CTRL+I`) in order to view the video statistics.
To set media player as VLC Media Player in the below examples, set the `player` argument of `MpegDashApplication` to 'vlc'.

In all the examples below, NeST will accept video input from a file named `video.mp4`.
This video file has to be placed in the same directory as the example program.
The encoded chunks will be generated and dumped in a folder named `mpeg-dash-encoded-chunks` in the same directory as the example program.

## 1. mpeg-dash-point-to-point-1.py
This program emulates a point to point network between two hosts `h1` and
`h2`. Here, `h2` acts as the MPEG-DASH streaming server and `h1` acts as the MPEG-DASH client.
The results of this MPEG-DASH video streaming experiment will be documented in the `examples/mpeg-dash/mpeg-dash-point-to-point-1(date-timestamp)_dump` folder. It contains a `README` which provides details about the sub-directories and files within this directory.

Additionally, Socket statistics (ss) will be gathered and stored in the same folder mentioned above. However, it's important to note that these socket statistics are collected as a formality and might not offer significant or useful information.

## 2. mpeg-dash-two-lans-connected-via-router.py
This program emulates two Local Area Network (LANs) connected via a router.
LAN-1 consists three hosts `h1` to `h3` connected to switch `s1`, and
LAN-2 consists three hosts `h4` to `h6` connected to switch `s2`. Switches
`s1` and `s2` are connected to each other via a router `r1`.
MPEG-DASH applications have been configured between the following client,server
pairs: (`h1`,`h4`) , (`h6`,`h2`).
The results of this MPEG-DASH video streaming experiment will be documented in the `examples/mpeg-dash/mpeg-dash-two-lans-connected-via-router(date-timestamp)_dump` folder. It  contains a `README` which provides details about the sub-directories and files within this directory.

Additionally, Socket statistics (ss) will be gathered and stored in the same folder mentioned above. However, it's important to note that these socket statistics are collected as a formality and might not offer significant or useful information.
