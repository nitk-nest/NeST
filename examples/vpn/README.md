# Virtual Private Network (VPN) Examples in NeST

This directory contains examples to demonstrate how to use Virtual Private Network (VPN) in `NeST`.

`IMPORTANT`

Before running the examples, you will need to install OpenVPN and Easy-RSA. You can do this by running the following command in your terminal:

```shell
sudo apt install openvpn easy-rsa
```

## 1. vpn-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and `h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1` to `h2` once using Using the VPN endpoint address and once using Using the public address, and the success/failure of these packets is reported. It is similar to `point-to-point-3.py` available in `examples/basic-examples`, the only difference is that we use `connect_vpn` API to create VPN tunnel between nodes.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: vpn-point-to-point-3.py -->
