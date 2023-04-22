# Mytraceroute (MTR)/traceroute Examples in NeST

This directory contains examples to demonstrate how to use Mytraceroute (MTR) and traceroute in `NeST`.

`IMPORTANT`

Before running the MTR examples, you will need to install mtr. You can do this by running the following command in your terminal:

```shell
sudo apt install mtr
```

## 1. mtr-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and `h2` via two routers `r1` and `r2`. Mytraceroute functionality is performed Five times from `h1` to `h2`and the result is reported. It is similar to `point-to-point-3.py` available in `examples/basic-examples`, the only difference is that Mytraceroute is performed between nodes instead of ping .

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: mtr-point-to-point-3.py -->


## 2. traceroute-point-to-point-3.py

This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. Traceroute is run from h1 to an interface
of h2. It is similar to `static-routing-point-to-point-3.py` available in
`examples/static-routing` , the only difference is that traceroute is used
instead of ping.
