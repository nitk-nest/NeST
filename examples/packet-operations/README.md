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

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-capture-point-to-point-3.py -->

## 2. packet-corruption-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. 20 ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` in `examples/address-helpers`. This program shows
the emulation of random noise to introduce an error at a random position
for a chosen percentage of packets.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-corruption-point-to-point-3.py -->

## 3. packet-duplication-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. 20 ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` in `examples/address-helpers`. This program shows
the emulation of packet duplication for a chosen percentage of packets.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-duplication-point-to-point-3.py -->

## 4. packet-loss-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. 20 ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` in `examples/address-helpers`. This program shows
how to add an independent loss probability to the packets outgoing from the
chosen network interface.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-loss-point-to-point-3.py -->

## 5. packet-ping-preload-point-to-point-3.py
This program emulates a point to point network that connects two hosts `h1`
and `h2` via two routers `r1` and `r2`. 20 ping packets are sent from `h1` to
`h2`. It is similar to `examples/address-helpers/ah-point-to-point-3.py`.
Out of 20 ping packets that are sent, the first 10 ping packets are sent
simultaneously without waiting for a reply from `h2`, and the remaining 10
ping packets are sent one by one. The success/failure of all ping packets is
reported. The ping preload option is used for sending the first 10 packets.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-ping-preload-point-to-point-3.py -->
