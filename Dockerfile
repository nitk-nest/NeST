# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

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
        bison

# Setup python virtual env
RUN python -m venv venv && source venv/bin/activate

# Install python dependencies
RUN pip install \
        junit2html \
        coverage \
        gitlint \
        pre-commit \
        pylint \
        pytest

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

FROM test as dev

WORKDIR /home
RUN git clone https://gitlab.com/nitk-nest/nest.git/
WORKDIR /home/nest/
RUN pip install .
