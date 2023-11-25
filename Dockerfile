# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

# Dockerfile to build image with dependecies required for testing nest on CI.

FROM ubuntu:20.04@sha256:8c38f4ea0b178a98e4f9f831b29b7966d6654414c1dc008591c6ec77de3bf2c9 as test

# Use bash by default instead of sh
SHELL ["/bin/bash", "-c"]

RUN apt update

# Install basic dependencies
RUN DEBIAN_FRONTEND=noninteractive apt -y install \
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

RUN groupadd quagga
RUN useradd -g quagga -s /bin/false quagga

# Install quagga from source
RUN wget https://github.com/Quagga/quagga/releases/download/quagga-1.2.4/quagga-1.2.4.tar.gz
RUN tar -xzf quagga-1.2.4.tar.gz
WORKDIR /quagga-1.2.4
RUN ./configure \
        --prefix=/usr \
        --sbindir=/usr/bin \
        --sysconfdir=/etc/quagga \
        --localstatedir=/run/quagga \
        --enable-exampledir=/usr/share/doc/quagga/examples \
        --enable-vtysh \
        --enable-isis-topology \
        --enable-netlink \
        --enable-snmp \
        --enable-tcp-zebra \
        --enable-irdp \
        --enable-pcreposix \
        --enable-multipath=64 \
        --enable-user=quagga \
        --enable-group=quagga \
        --enable-configfile-mask=0640 \
        --enable-logfile-mask=0640
RUN make
RUN make install
WORKDIR /
RUN mkdir -p /run/quagga
RUN mkdir -p /etc/quagga
RUN ldconfig
RUN chown quagga:quagga /run/quagga
RUN chown quagga:quagga /etc/quagga
RUN echo $' \n\
    zebra=yes \n\
    ospfd=yes \n\
    ripd=yes \n\
    isisd=yes ' >> /etc/quagga/daemons

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
