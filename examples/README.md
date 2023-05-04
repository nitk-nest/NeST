# NeST Examples

This directory contains several examples that demonstrate APIs and different
features that are supported in NeST. The table shown below depicts which APIs or
features of NeST are used in every sub-directory inside `examples` directory.
A detailed README is provided in every sub-directory in `examples`.

We recommend the users to traverse through the examples in the following order
to quickly learn and use NeST APIs and its features.

1. [basic-examples](./basic-examples/README.md)
2. [config-options](./config-options/README.md)
3. [ipv6](./ipv6/README.md) (optional)
4. [address-helpers](./address-helpers/README.md)
5. [packet-operations](./packet-operations/README.md) (optional)
6. [udp](./udp/README.md) (optional)
7. [tcp](./tcp/README.md) (optional)
8. [qdiscs](./tcp/README.md) (optional)
9. [routing](./routing/README.md) (optional)
10. [coap](./coap/README.md) (optional)

| Examples          | Basic APIs         | Address Helpers    | Routing Helpers    | Ping Application   | UDP Flows          | TCP Flows          |
|-------------------|--------------------|--------------------|--------------------|--------------------|--------------------|--------------------|
| basic-examples    | :white_check_mark: | :x:                | :x:                | :white_check_mark: | :x:                | :x:                |
| config-options    | :white_check_mark: | :x:                | :x:                | :white_check_mark: | :x:                | :x:                |
| ipv6              | :white_check_mark: | :x:                | :x:                | :white_check_mark: | :x:                | :x:                |
| address-helpers   | :white_check_mark: | :white_check_mark: | :x:                | :white_check_mark: | :x:                | :x:                |
| packet-operations | :white_check_mark: | :white_check_mark: | :x:                | :white_check_mark: | :x:                | :x:                |
| udp               | :white_check_mark: | :white_check_mark: | :x:                | :x:                | :white_check_mark: | :x: |
| tcp               | :white_check_mark: | :white_check_mark: | :x:                | :x:                | :white_check_mark: | :white_check_mark: |
| qdiscs               | :white_check_mark: | :white_check_mark: | :x:                | :x:                | :white_check_mark: | :white_check_mark: |
| routing           | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :x:                | :x:                |
|coap               | :white_check_mark: | :white_check_mark: | :x:                | :x:                | :x:                | :x:                |
