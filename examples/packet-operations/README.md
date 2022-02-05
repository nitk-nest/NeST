# Examples to show different packet level operations supported in NeST

This directory contains the examples to show different packet level operations
supported in `NeST`.

`IMPORTANT`
The example `packet-capture-point-to-point-3.py` requires `tcpdump` to be pre-
installed. It can be installed on debian based systems as:

```shell
sudo apt install tcpdump
```

## 1. packet-capture-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. 10 ping packets are sent from `h1` to
`h2`. It is similar to `ah-point-to-point-3.py` in `examples/address-helpers`.
This program shows how to capture packets at `h2` by using `tcpdump`.

## 2. packet-corruption-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. 20 ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` in `examples/address-helpers`. This program shows
the emulation of random noise to introduce an error at a random position
for a chosen percentage of packets.

## 3. packet-loss-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. 20 ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` in `examples/address-helpers`. This program shows
how to add an independent loss probability to the packets outgoing from the
chosen network interface.
