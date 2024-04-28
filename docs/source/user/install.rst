.. SPDX-License-Identifier: GPL-2.0-only
    Copyright (c) 2019-2021 NITK Surathkal

.. highlight:: console

Installation
============

Installing **NeST** is a two-step process. The first step is to install NeST
python package itself using pip, and the next step is to install the necessary
external dependencies of NeST.

Note that NeST is supported only for **Linux** systems currently.

1. Installing NeST python package
---------------------------------

First, ensure that you have python version 3.6 or above in your system::

    $ python3 -V

Next, ensure that you have pip installed (to install python3 packages).
It can be installed from your Linux Package Manager. For example,
this is the command to install pip in Ubuntu::

    $ sudo apt install python3-pip

After installing pip, make sure you also upgrade it::

    $ python3 -m pip install -U pip

Below are the three approaches to install NeST python package:

i) From PyPi
^^^^^^^^^^^^

This is the recommended way to install for most users of NeST.
The below command will install NeST from
https://pypi.org/project/nitk-nest/ (Python Package Index)::

    $ python3 -m pip install nest

ii) From docker
^^^^^^^^^^^^^^^
You may use docker to quickly get started with NeST. The docker image has all the necessary dependencies installed

1. Install the docker engine.

    Docker engine is required to pull and run docker images. You can find the
    the installation instructions for docker for Linux distros `here <https://docs.docker.com/engine/install/#server>`__

2. Pull the docker image::

    $ docker pull nestnitk/nest-docker:<tag>

    Here `<tag>` can be one of:
    1. `latest` if you want to get the docker image with the version of NeST
        that corresponds to the changes on the master branch.
    2. A specific release version of NeST(for example, v0.4).
       You can find the list of NeST versions here: https://gitlab.com/nitk-nest/nest/-/tags.
       Note that there are no docker images for version below v0.4.

3. Run the docker image::

    $ docker run --privileged -it nestnitk/nest-docker

    This command will launch a shell into the NeST container and
    you will be inside the NeST directory by default. You can use this
    shell to run any commands/programs as you would on a normal terminal.
    This container already has NeST installed along with all the dependencies for you
    which can be verified by running one of the NeST scripts under the `examples` folder.

iii) From source
^^^^^^^^^^^^^^^^

Follow this approach if you want to contribute to NeST development or want the
latest source code with unreleased features.

1. Clone the official git repository::

    $ git clone https://gitlab.com/nitk-nest/nest.git

2. Install via pip

    If you are developing or contributing to NeST development, then it is better
    to install NeST in editable mode. In editable mode, your code changes are
    instantly propagated to the library code without reinstalling::

        $ python3 -m pip install -e .

    If you are not developing, then run the below command::

        $ python3 -m pip install .


2. Install dependencies
-----------------------

NeST is an orchestration tool that relies on various network tools for its APIs.
Below are the list of dependencies NeST requires. You do not need to install all
of them. The dependencies you install will depend on your use case and how you
would like to use NeST.

**Core dependencies** will be marked as bold and *Optional dependencies*
will be marked in italics.

You can skip all the following steps if you are using the docker image of NeST.

1. Ensure **iproute2** suite is installed with your kernel

::

    $ ip -V
    ip utility, iproute2-ss200127

2. Ensure **ping** is installed

::

    $ ping -V
    ping from iputils s20190709


3. Install **netperf**

    You can check if netperf is installed by running the command::

        $ netperf -V
        Netperf version 2.7.0

    If netperf is not installed, then it can be obtained from your
    Linux distribution packages.
    For Ubuntu run::

        $ sudo apt install netperf

    Minimum version of netperf supported is 2.6.0

4. Install *iperf3*

    This is an optional dependency. You can install it if you want
    NeST to internally use iperf3 to generate flows.

    You can check if iperf3 is installed by running the command::

        $ iperf3 -v
        iperf 3.7 (cJSON 1.5.2)
        Linux your-system 5.4.0-51-generic #56-Ubuntu SMP Mon Oct 5 14:28:49 UTC  2020 x86_64

    If iperf3 is not installed, then it can be obtained from your Linux
    distribution packages. For Ubuntu run::

        $ sudo apt install iperf3

5. Install and setup a *dynamic routing suite* (optional)

    This is an optional dependency. You can install either *Frrouting*
    **or** *Quagga* if you want to use dynamic routing APIs in NeST.

    a) *Frrouting*

        To install Frrouting on Ubuntu run::

            $ sudo apt install frr

        or follow the steps here: https://deb.frrouting.org

    b) Quagga

        Quagga can be obtained from your Linux distribution packages.
        For Ubuntu run::

            $ sudo apt install quagga quagga-doc

        Edit `/etc/quagga/daemons` with an editor using sudo and turn on zebra,
        ripd, ospfd and isisd by changing the following lines:

        .. code-block:: bash

            zebra=no -> zebra=yes
            ripd=no -> ripd=yes
            ospfd=no -> ospfd=yes
            isisd=no -> isisd=yes

        If the `daemons` file doesn't exist create one and add the following
        lines to the file:

        .. code-block:: bash

            zebra=yes
            bgpd=no
            ospfd=yes
            ospf6d=no
            ripd=yes
            ripngd=no
            isisd=yes
            babeld=no

        **Note**: Ensure that a quagga owned directory named 'quagga' exists
        under /run. If it doesn't exist run::

            $ sudo mkdir /run/quagga
            $ sudo chown quagga /run/quagga

6. Install dependencies for *MPEG-DASH video streaming* (optional)

    These dependencies need to be installed if you want to use the
    MPEG-DASH video streaming APIs in NeST. For using MPEG-DASH APIs,
    GPAC MP4 Client is required for video encoding. This API supports
    video playback via GPAC MP4 Client and VLC Media Player.

    a) *GPAC MP4 Client*

        To install GPAC on Ubuntu run::

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
            $ sudo make
            $ sudo make install

        **Note**: Ensure that the installed `gpac` version is `2.2 or above`
        by typing `gpac` in the terminal.

        In case you want to dive into the details of GPAC installation,
        feel free to read their documentation at https://github.com/gpac/gpac/wiki/GPAC-Build-Guide-for-Linux


    b) VLC Media Player

        To install VLC on Ubuntu run::

            $ sudo apt install vlc
