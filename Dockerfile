# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

# Dockerfile to build image with dependecies required for testing nest on CI.

FROM ubuntu:20.04@sha256:b2339eee806d44d6a8adc0a790f824fb71f03366dd754d400316ae5a7e3ece3e as test

# Use bash by default instead of sh
SHELL ["/bin/bash", "-c"]

# Install basic dependencies
RUN apt -y upgrade
RUN apt -y update
RUN apt -y install build-essential
RUN apt -y install git
RUN apt -y install wget
RUN apt -y install gawk
RUN apt -y install libreadline6-dev
RUN apt -y install iproute2
RUN apt -y install iputils-ping

# Install python
RUN apt install -y python3 python3-pip python3-venv
# Sym link for python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Setup python virtual env
RUN python -m venv venv
RUN source venv/bin/activate

# Install python dependencies
RUN pip install junit2html
RUN pip install coverage
RUN pip install gitlint
RUN pip install pre-commit
RUN pip install pylint
RUN pip install pytest

# Install netperf
RUN apt -y install netperf

# Install quagga from source
RUN groupadd quagga
RUN useradd -g quagga -s /bin/false quagga
RUN apt install -y libc-ares-dev
RUN DEBIAN_FRONTEND=noninteractive apt install -y pkg-config
RUN apt install -y snmpd snmp libsnmp-dev
RUN wget https://github.com/Quagga/quagga/releases/download/quagga-1.2.4/quagga-1.2.4.tar.gz
RUN tar -xzf quagga-1.2.4.tar.gz
WORKDIR /quagga-1.2.4
RUN ./configure --prefix=/usr --sbindir=/usr/bin --sysconfdir=/etc/quagga --localstatedir=/run/quagga --enable-exampledir=/usr/share/doc/quagga/examples --enable-vtysh --enable-isis-topology --enable-netlink --enable-snmp --enable-tcp-zebra --enable-irdp --enable-pcreposix --enable-multipath=64 --enable-user=quagga --enable-group=quagga --enable-configfile-mask=0640 --enable-logfile-mask=0640
RUN make
RUN make install
WORKDIR /
RUN mkdir -p  /run/quagga
RUN mkdir -p /etc/quagga
RUN ldconfig
RUN chown quagga:quagga /run/quagga
RUN chown quagga:quagga /etc/quagga
RUN echo $' \n\
zebra=yes \n\
ospfd=yes \n\
ripd=yes \n\
isisd=yes ' >> /etc/quagga/daemons

# Install FRR
RUN apt install -y frr
RUN mkdir -p /run/frr
RUN chown frr /run/frr

# Install ethtool
RUN apt install -y ethtool

# Install iperf3
RUN apt install -y iperf3

# Installs lsmod and other kernel module utilites
RUN apt install -y kmod

# Install tcpdump
RUN apt install -y tcpdump

# Install tshark
RUN DEBIAN_FRONTEND=noninteractive apt install -y tshark

# Install bird
RUN git clone --depth 1 --branch 2.0.10 https://gitlab.nic.cz/labs/bird.git
WORKDIR /bird
RUN apt install -y autoconf flex bison
RUN autoreconf
RUN ./configure
RUN make
RUN make install
WORKDIR /

FROM test as dev

WORKDIR /home
RUN git clone https://gitlab.com/nitk-nest/nest.git/
WORKDIR /home/nest/
RUN pip install .
