# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2024 NITK Surathkal

# Dockerfile to build image with dependecies required for testing nest on CI.

FROM ubuntu:22.04@sha256:bcc511d82482900604524a8e8d64bf4c53b2461868dac55f4d04d660e61983cb as test

# Use bash by default instead of sh
SHELL ["/bin/bash", "-c"]

RUN apt-get update

# Install basic dependencies
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install \
        build-essential \
        git \
        wget \
        gawk \
        libreadline6-dev \
        iproute2 \
        iputils-ping \
        python3 \
        python3-pip \
        python3-venv \
        python-is-python3 \
        netperf \
        iperf3 \
        ethtool \
        kmod \
        tcpdump \
        tshark \
        libc-ares-dev \
        pkg-config \
        snmpd \
        snmp \
        libsnmp-dev \
        frr \
        autoconf \
        flex \
        bison \
        mptcpize \
        vlc

# Install prerequisite dependencies for building GPAC (Media Player and Encoder for MPEG-DASH streams)
# Reference: https://github.com/gpac/gpac/blob/master/build/docker/ubuntu-deps.Dockerfile
RUN apt -yqq update
RUN apt-get install -y --no-install-recommends \
        fakeroot \
        dpkg-dev \
        devscripts \
        debhelper \
        ccache
RUN apt install -y --no-install-recommends \
        zlib1g-dev \
        libfreetype6-dev \
        libjpeg62-dev \
        libpng-dev \
        libmad0-dev \
        libfaad-dev \
        libogg-dev \
        libvorbis-dev \
        libtheora-dev \
        liba52-0.7.4-dev \
        libavcodec-dev \
        libavformat-dev \
        libavutil-dev \
        libswscale-dev \
        libavdevice-dev \
        libnghttp2-dev \
        libopenjp2-7-dev \
        libcaca-dev \
        libxv-dev \
        x11proto-video-dev \
        libgl1-mesa-dev \
        libglu1-mesa-dev \
        x11proto-gl-dev \
        libxvidcore-dev \
        libssl-dev \
        libjack-jackd2-dev \
        libasound2-dev \
        libpulse-dev \
        libsdl2-dev \
        dvb-apps mesa-utils

# Set XDG_RUNTIME_DIR to /tmp to avoid permission issues
ENV XDG_RUNTIME_DIR=/tmp

# Setup python virtual env
RUN python -m venv venv && source venv/bin/activate

# Install python dependencies
RUN pip install \
        junit2html \
        coverage \
        gitlint \
        pre-commit \
        pylint \
        pytest \
        colorama

# Configure FRR
RUN mkdir -p /run/frr
RUN chown frr /run/frr

# Install bird
RUN git clone --depth 1 --branch v2.0.10 https://gitlab.nic.cz/labs/bird.git
WORKDIR /bird
RUN autoreconf
RUN ./configure
RUN make
RUN make install

# Install GPAC (Media Player and Encoder for MPEG-DASH streams)
WORKDIR /home
RUN git clone https://github.com/gpac/gpac.git
WORKDIR /home/gpac
RUN ./configure
RUN make
RUN make install

FROM test as dev

WORKDIR /home
RUN git clone https://gitlab.com/nitk-nest/nest.git/
WORKDIR /home/nest/
RUN pip install .
