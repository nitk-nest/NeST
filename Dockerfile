# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2026 NITK Surathkal

# Dockerfile to build image with dependecies required for testing nest on CI.

FROM ubuntu:22.04@sha256:bcc511d82482900604524a8e8d64bf4c53b2461868dac55f4d04d660e61983cb AS test

# Use bash by default instead of sh
SHELL ["/bin/bash", "-c"]

ENV XDG_RUNTIME_DIR=/tmp
ENV DEBIAN_FRONTEND=noninteractive

# Consolidate all apt-get installations into a single layer and clean up the cache
# Notes:
        # Install basic dependencies
        # Install prerequisite dependencies for building GPAC (Media Player and Encoder for MPEG-DASH streams)
        # Reference: https://github.com/gpac/gpac/blob/master/build/docker/ubuntu-deps.Dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
        # Basic Dependencies & Networking Tools
        build-essential git wget gawk libreadline6-dev iproute2 iputils-ping \
        python3 python3-pip python3-venv python-is-python3 netperf iperf3 \
        ethtool kmod tcpdump tshark libc-ares-dev pkg-config snmpd snmp \
        libsnmp-dev frr autoconf flex bison mptcpize vlc gnuplot \
        openvpn easy-rsa mtr traceroute \
        # GPAC Dependencies
        fakeroot dpkg-dev devscripts debhelper ccache zlib1g-dev libfreetype6-dev \
        libjpeg62-dev libpng-dev libmad0-dev libfaad-dev libogg-dev libvorbis-dev \
        libtheora-dev liba52-0.7.4-dev libavcodec-dev libavformat-dev libavutil-dev \
        libswscale-dev libavdevice-dev libnghttp2-dev libopenjp2-7-dev libcaca-dev \
        libxv-dev x11proto-video-dev libgl1-mesa-dev libglu1-mesa-dev x11proto-gl-dev \
        libxvidcore-dev libssl-dev libjack-jackd2-dev libasound2-dev libpulse-dev \
        libsdl2-dev dvb-apps mesa-utils \
        # SIPp Dependencies
        g++ gcc dh-autoreconf ncurses-dev libpcap-dev libncurses5-dev libsctp-dev \
        lksctp-tools libgsl-dev cmake \
    && rm -rf /var/lib/apt/lists/*

# Configure FRR
RUN mkdir -p /run/frr && chown frr /run/frr

# Setup python virtual environment and set PATH
ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install python dependencies without saving the pip download cache
RUN pip install --no-cache-dir \
        junit2html coverage gitlint pre-commit pylint pytest colorama

# Compile Bird, GPAC, and SIPp from source
# Grouped into a single working directory. Source code is deleted in the same step it is compiled to save layer space.
WORKDIR /src

RUN git clone --depth 1 --branch v2.0.10 https://gitlab.nic.cz/labs/bird.git && \
    cd bird && autoreconf && ./configure && make && make install && \
    cd /src && rm -rf bird

RUN git clone --depth 1 https://github.com/gpac/gpac.git && \
    cd gpac && ./configure && make && make install && \
    cd /src && rm -rf gpac

RUN git clone -b v3.7.7 --depth 1 https://github.com/SIPp/sipp.git && \
    cd sipp && cmake . -DUSE_SSL=1 -DUSE_SCTP=1 -DUSE_PCAP=1 -DUSE_GSL=1 && make all && make install && \
    cd /src && rm -rf sipp

# -------------------------------------------------------------------
# Dev Stage
# -------------------------------------------------------------------
FROM test AS dev

WORKDIR /home
RUN git clone https://gitlab.com/nitk-nest/nest.git/
WORKDIR /home/nest/
RUN pip install --no-cache-dir .
