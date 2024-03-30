# Examples to demonstrate how to emulate SIP in NeST

This directory contains the following example to understand how SIP application can be emulated in `NeST`. `SipApplication` API is used in these examples to configure a SIP application between a pair of nodes.

## Scenario XML files
The subdirectory `scenario-xml-files` contains some of the XML files provided by sipp for SIP traffic emulation and they can be used in NeST SIP emulation with the "xml" scenario argument. The XML files can be modified or new XML files can be used to create custom scenarios for the emulation. Feel free to read more about how to write Scenario XML files at [https://sipp.readthedocs.io/en/latest/scenarios/ownscenarios.html](https://sipp.readthedocs.io/en/latest/scenarios/ownscenarios.html).

## Pre-requisites
`IMPORTANT`
It is strongly recommended that you run these SIP examples on systems with Ubuntu version `22.04 or above`.
All the examples listed below require SIPp to be pre-installed in your machine.

SIPp can be installed as follows:
```shell
$ sudo apt -yqq update
$ sudo apt install -y --no-install-recommends \
        pkg-config \
        g++ \
        gcc \
        dh-autoreconf \
        ncurses-dev \
        build-essential \
        libssl-dev \
        libpcap-dev \
        libncurses5-dev \
        libsctp-dev \
        lksctp-tools \
        libgsl-dev \
        cmake
$ git clone https://github.com/SIPp/sipp.git
$ cd sipp/
$ sudo cmake . -DUSE_SSL=1 -DUSE_SCTP=1 -DUSE_PCAP=1 -DUSE_GSL=1
$ sudo make all
$ sudo make install

```
In case you want to dive into the details of SIPp installation,
feel free to read their documentation at [https://sipp.readthedocs.io/en/latest/installation.html](https://sipp.readthedocs.io/en/latest/installation.html)

## 1. sip-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`.
Here, `h1` acts as the SIP client and `h2` acts as the SIP server.
The results of this SIP experiment will be documented in the `examples/sip/sip-point-to-point-3(date-timestamp)_dump` folder. It  contains a `README` which provides details about the sub-directories and files within this directory.

## 2. sip-two-lans-connected-via-router.py
This program emulates two Local Area Network (LANs) connected via a router.
LAN-1 consists four hosts `h1` to `h4` connected to switch `s1`, and
LAN-2 consists four hosts `h5` to `h8` connected to switch `s2`. Switches
`s1` and `s2` are connected to each other via a router `r1`.
There are 4 SIP applications running in this example:
In first application, basic scenario is emulated using `h1` as client and `h5` as server by passing "basic" as `scenario` argument to `SipApplication`.
In second application, branch scenario is emulated using `h2` as client and `h6` as server by passing "branch" as `scenario` argument to `SipApplication`.
In third application, basic scenario is emulalated using `h3` as client and `h5` as server by passing "xml" as `scenario` argument and passing "uac.xml" xml
file as `client_xml` argument to `SipApplication`.
In fourth application, branch scenario is emulalated using `h4` as client and `h7` as server by passing "xml" as `scenario` argument, passing "branchc.xml"
xml file as `client_xml` argument and "branchs.xml" as `server_xml` argument to `SipApplication`.
The results of this SIP experiment will be documented in the `examples/sip/sip-two-lans-connected-via-router(date-timestamp)_dump` folder. It  contains a `README` which provides details about the sub-directories and files within this directory.
