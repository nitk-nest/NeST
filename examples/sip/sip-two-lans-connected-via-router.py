# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2024 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
import os
from pathlib import Path
from nest.topology import *
from nest.experiment import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

# This program emulates two Local Area Networks (LANs) connected via a router.
# LAN-1 consists three hosts `h1` to `h3` connected to switch `s1`, and
# LAN-2 consists three hosts `h4` to `h6` connected to switch `s2`. Switches
# `s1` and `s2` are connected to each other via a router `r1`.

# There are total 4 SIP applications running in this example.

# In first application, basic scenario is emulated using h1 as client and h5
# as server by passing "basic" as `scenario` argument to `SipApplication`.

# In second application, branch scenario is emulated using h2 as client and h6
# as server by passing "branch" as `scenario` argument to `SipApplication`.

# In third application, basic scenario is emulalated using h3 as client and h5
# as server by passing "xml" as `scenario` argument and passing "uac.xml" xml
# file as `client_xml` argument to `SipApplication`.

# In fourth application, branch scenario is emulalated using h4 as client and
# h7 as server by passing "xml" as `scenario` argument, passing "branchc.xml"
# xml file as `client_xml` argument and "branchs.xml" as `server_xml` argument
# to `SipApplication`.

###########################################################################
#                       Network Topology                                  #
#           LAN-1                           LAN-2                         #
#   h1 -------------------|                 |----------------------- h5   #
#                         |                 |                             #
#   h2 ---------------|   |                 |    |------------------ h6   #
#                     |   |                 |    |                        #
#                     |_ _|____          ___|__ _|                        #
#                       |      |        |      |                          #
#                       |  s1  |---r1---|  s2  |                          #
#                      _|______|        |______|_                         #
#                     |   |                 |    |                        #
#                     |   |                 |    |                        #
#   h3 ---------------|   |                 |    |------------------ h7   #
#                         |                 |                             #
#   h4 -------------------|                 |----------------------- h8   #
#                                                                         #
#     <- 100mbit, 1ms ->   <- 10mbit, 10ms ->    <- 100mbit, 1ms ->       #
#                                                                         #
###########################################################################


# Create six hosts 'h1' to 'h8'
h1 = Node("h1")
h2 = Node("h2")
h3 = Node("h3")
h4 = Node("h4")
h5 = Node("h5")
h6 = Node("h6")
h7 = Node("h7")
h8 = Node("h8")

# Create two switches 's1' and 's2'
s1 = Switch("s1")
s2 = Switch("s2")

# Create a router 'r1'
r1 = Router("r1")

# Define the networks (subnets)
n1 = Network("192.168.1.0/24")
n2 = Network("192.168.2.0/24")

# Connect LAN-1 hosts (h1 to h4) to switch s1 on network n1
(eth1, est1a) = connect(h1, s1, network=n1)
(eth2, est1b) = connect(h2, s1, network=n1)
(eth3, est1c) = connect(h3, s1, network=n1)
(eth4, est1d) = connect(h4, s1, network=n1)

# Connect LAN-2 hosts (h5 to h8) to switch s2 on network n2
(eth5, est2a) = connect(h5, s2, network=n2)
(eth6, est2b) = connect(h6, s2, network=n2)
(eth7, est2c) = connect(h7, s2, network=n2)
(eth8, est2d) = connect(h8, s2, network=n2)

# Connect switches to router r1
(est1e, etr1a) = connect(s1, r1, network=n1)
(est2e, etr1b) = connect(s2, r1, network=n2)

# Automatically assign all addresses using helper
AddressHelper.assign_addresses()

# Set the attributes of the links between hosts and switches
eth1.set_attributes("100mbit", "1ms")
eth2.set_attributes("100mbit", "1ms")
eth3.set_attributes("100mbit", "1ms")
eth4.set_attributes("100mbit", "1ms")
eth5.set_attributes("100mbit", "1ms")
eth6.set_attributes("100mbit", "1ms")
eth7.set_attributes("100mbit", "1ms")
eth8.set_attributes("100mbit", "1ms")

# Set the attributes of the links between `r1` and switches
etr1a.set_attributes("10mbit", "10ms")
etr1b.set_attributes("10mbit", "10ms")

# Set the default routes for hosts `h1`, `h2`, `h3` and `h4` via `etr1a`
h1.add_route("DEFAULT", eth1, etr1a.address)
h2.add_route("DEFAULT", eth2, etr1a.address)
h3.add_route("DEFAULT", eth3, etr1a.address)
h4.add_route("DEFAULT", eth4, etr1a.address)

# Set the default routes for hosts `h5`, `h6`, `h7` and `h8` via `etr1b`
h5.add_route("DEFAULT", eth5, etr1b.address)
h6.add_route("DEFAULT", eth6, etr1b.address)
h7.add_route("DEFAULT", eth7, etr1b.address)
h8.add_route("DEFAULT", eth8, etr1b.address)

# This example runs default branch scenario
exp = Experiment("sip-two-lans-connected-via-router")

# Set the experiment duration in seconds.
duration = 40

# Set target callrate for SIP Application,
# NeST uses target callrate as 10 if this argument is not passed.
callrate = 12

# There are three scenario options that can be passed as argument:
#   1) basic
#   2) branch
#   3) xml

# If scenario 3 is passed as scenario then next two arguments are for
# server_xml file and client xml file, if any of the argument is omitted.
# default scenario is used for it.

# create a SIP application to run "basic" scenario using h1 as client
# and h5 as server.
basic_app = SipApplication(
    h1,  # client namespace
    h5,  # server namespace
    eth1.get_address(),  # client IP
    eth5.get_address(),  # server IP
    5050,  # server PORT
    duration,  # duration in seconds
    "basic",  # scenario
    callrate=callrate,  # callrate (calls per second)
)
exp.add_sip_application(basic_app)

# create a SIP application to run "branch" scenario using h2 as client
# and h6 as server. (using different host for server so that it runs
# branch scenario for server)
branch_app = SipApplication(
    h2,  # client namespace
    h6,  # server namespace
    eth2.get_address(),  # client IP
    eth6.get_address(),  # server IP
    5050,  # server PORT
    duration,  # duration in seconds
    "branch",  # scenario
    callrate=callrate,  # callrate (calls per second)
)
exp.add_sip_application(branch_app)

# xml_dir contains some integrated scenario xml files.
xml_dir = os.path.join(Path(os.path.abspath(__file__)).parent, "scenario-xml-files")

cli_xml = os.path.join(xml_dir, "uac.xml")

# create a SIP application to run "xml" scenario using h3 as client
# and h5 as server with "uac" (Basic) xml file for client xml
basic_xml_app = SipApplication(
    h3,  # client namespace
    h5,  # server namespace
    eth3.get_address(),  # client IP
    eth5.get_address(),  # server IP
    5050,  # server PORT
    duration,  # duration in seconds
    "xml",  # scenario
    client_xml=cli_xml,  # path to xml file to run SIP client
    callrate=callrate,  # callrate (calls per second)
)
exp.add_sip_application(basic_xml_app)

cli_xml = os.path.join(xml_dir, "branchc.xml")
server_xml = os.path.join(xml_dir, "branchs.xml")

# create a SIP application to run "xml" scenario using h4 as client
# and h7 as server with "branch" (Branch Scenario) xml files for client_xml and
# server_xml.
branch_xml_app = SipApplication(
    h4,  # client namespace
    h7,  # server namespace
    eth4.get_address(),  # client IP
    eth7.get_address(),  # server IP
    5050,  # server PORT
    duration,  # duration in seconds
    "xml",  # scenario
    server_xml=server_xml,  # path to xml file to run SIP server
    client_xml=cli_xml,  # path to xml file to run SIP client
    callrate=callrate,  # callrate (calls per second)
)
exp.add_sip_application(branch_xml_app)

exp.run()
