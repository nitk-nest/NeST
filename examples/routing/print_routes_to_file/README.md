This directory contains an example which emulates point to point networks that
connect two hosts `h1` and `h2` via a router `r1` and prints the routes
obtained from the routing table of the node 'r1' to a file.

## 1. print-routes-point-to-point-2.py

This program emulates point to point networks that connect two hosts `h1` and
`h2` via a router `r1`. Five ping packets are sent from `h1` to `h2`, and the
success/failure of these packets is reported. It also prints the routes from
the routing table of a router `r1`.

The routes are dumped into three files. The routes of the `eth1a` interface of
the node `r1` are dumped to `route_info_of_interface_r1-h2-0.json`. Similarly
the routes of `eth1b` interface onto `route_info_of_interface_r1-h2-0.json`.
Finally it prints all the routes from the node `r1` into another file.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: print-routes-point-to-point-2.py -->
