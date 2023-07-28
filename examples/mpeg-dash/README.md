# Examples to demonstrate how to stream videos using MPEG DASH in NeST

This directory contains the following example to understand how videos can be streamed using MPEG DASH in `NeST`. `MpegDashApplication` API is used in these examples to configure stream video between a pair of nodes.


`IMPORTANT`
It is strongly recommended that you run these MPEG-DASH examples on systems with Ubuntu version `22.04 or above`.
All the examples listed below require GPAC MP4 Client to be pre-installed in your machine.

GPAC MP4 Client can be installed as follows:
```shell
$ sudo apt -yqq update
$ sudo apt install -y --no-install-recommends \
fakeroot dpkg-dev devscripts debhelper ccache \
zlib1g-dev libfreetype6-dev libjpeg62-dev \
libpng-dev libmad0-dev libfaad-dev libogg-dev \
libvorbis-dev libtheora-dev liba52-0.7.4-dev \
libavcodec-dev libavformat-dev libavutil-dev \
libswscale-dev libavdevice-dev libnghttp2-dev \
libopenjp2-7-dev libcaca-dev libxv-dev \
x11proto-video-dev libgl1-mesa-dev libglu1-mesa-dev \
x11proto-gl-dev libxvidcore-dev libssl-dev \
libjack-jackd2-dev libasound2-dev libpulse-dev \
libsdl2-dev dvb-apps mesa-utils

$ git clone https://github.com/gpac/gpac.git
$ cd gpac/
$ ./configure
$ sudo make -j $(nproc)
$ make -j $(nproc) install

```
Ensure that the installed `gpac` version is `2.2 or above`.

In case you want to dive into the details of GPAC installation,
feel free to read their documentation at [https://github.com/gpac/gpac/wiki/GPAC-Build-Guide-for-Linux](https://github.com/gpac/gpac/wiki/GPAC-Build-Guide-for-Linux)


The installation command for VLC Media Player is as follows:

```shell
$ sudo apt install vlc
```

In case you use GPAC MP4 Client for playback then NeST will generate plots of the video streaming statistics and also generate a JSON file of the same.

In case you use VLC Media Player, then while the video is playing you will have to navigate to `Tools > Media Information > 'Statistics' Tab` (or use keyboard shortcut `CTRL+I`) in order to view the video statistics.

To set the media player as GPAC MP4 Client or VLC Media Player in the MPEG-DASH examples, set the `player` argument of `MpegDashApplication` to 'gpac' or 'vlc' respectively.

In all the examples below, NeST will accept video input from a file named `video.mp4`.
This video file has to be placed in the same directory as the example program.
If the video file specified above is not present, the API will automatically resort to
downloading a sample 15-second video from the Internet as a fallback mechanism.

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
