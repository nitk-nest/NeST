# Examples to show different packet level operations supported in NeST

This directory contains the examples to show different packet level operations
supported in `NeST`.

`IMPORTANT`
The example `packet-capture-point-to-point-3.py` requires `tcpdump` to be pre-
installed. It can be installed on debian based systems as:

```shell
sudo apt install tcpdump
```

## 1. packet-capture-point-to-point-3-tcpdump.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. 10 ping packets are sent from `h1` to
`h2`. It is similar to `ah-point-to-point-3.py` in `examples/address-helpers`.
This program shows how to capture packets at `h2` by using `tcpdump`. Output
of the details of the packets captured at the `eth2` interface of `h2` is then
displayed on the console.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-capture-point-to-point-3-tcpdump.py -->

## 2. packet-capture-point-to-point-3-tshark.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. 10 ping packets are sent from `h1` to
`h2`. It is similar to `ah-point-to-point-3.py` in `examples/address-helpers`.
This program shows how to capture packets at `h2` by using `tshark`. The
details of the packets captured at the `eth2` interface of `h2` are then
written into `packet_capture.pcap` file.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-capture-point-to-point-3-tshark.py -->

## 3. packet-corruption-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. 20 ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` in `examples/address-helpers`. This program shows
the emulation of random noise to introduce an error at a random position
for a chosen percentage of packets.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-corruption-point-to-point-3.py -->

## 4. packet-delay-distribution-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. 20 ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` in `examples/address-helpers`. This program shows how
to use different delay distribution options using NeST.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-delay-distribution-point-to-point-3.py -->

## 5. packet-duplication-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. 20 ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` in `examples/address-helpers`. This program shows
the emulation of packet duplication for a chosen percentage of packets.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-duplication-point-to-point-3.py -->

## 6. packet-loss-gemodel-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. 20 ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` in `examples/address-helpers`. This program shows
how to add an loss probability according to  the  Gilbert-Elliot  loss  model
or  its  special  cases (Gilbert,  Simple  Gilbert and  Bernoulli) to the
packets outgoing from the chosen network interface.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-loss-gemodel-point-to-point-3.py -->

## 7. packet-ping-preload-point-to-point-3.py
This program emulates a point to point network that connects two hosts `h1`
and `h2` via two routers `r1` and `r2`. 20 ping packets are sent from `h1` to
`h2`. It is similar to `examples/address-helpers/ah-point-to-point-3.py`.
Out of 20 ping packets that are sent, the first 10 ping packets are sent
simultaneously without waiting for a reply from `h2`, and the remaining 10
ping packets are sent one by one. The success/failure of all ping packets is
reported. The ping preload option is used for sending the first 10 packets.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-ping-preload-point-to-point-3.py -->

## 8. packet-loss-state-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. 20 ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` in `examples/address-helpers`. This program shows
how to add an loss probability using Markov model having four states to the
packets outgoing from the chosen network interface.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-loss-state-point-to-point-3.py -->

## 9. packet-ping-preload-point-to-point-3.py
This program emulates a point to point network that connects two hosts `h1`
and `h2` via two routers `r1` and `r2`. 20 ping packets are sent from `h1` to
`h2`. It is similar to `examples/address-helpers/ah-point-to-point-3.py`.
Out of 20 ping packets that are sent, the first 10 ping packets are sent
simultaneously without waiting for a reply from `h2`, and the remaining 10
ping packets are sent one by one. The success/failure of all ping packets is
reported. The ping preload option is used for sending the first 10 packets.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-ping-preload-point-to-point-3.py -->

## 10. packet-reordering-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. 20 ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` in `examples/address-helpers`. This program shows the
emulation of packet reordering for a chosen percentage of packets.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: packet-reordering-point-to-point-3.py -->
