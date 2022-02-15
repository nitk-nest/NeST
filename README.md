# NeST: Network Stack Tester

[![pipeline status](https://gitlab.com/nitk-nest/nest/badges/master/pipeline.svg)](https://gitlab.com/nitk-nest/nest/-/commits/master)

`NeST` is a python3 package that handles testbed setup, testbed configuration,
collecting and visualizing data by providing a user friendly API, addressing
common issues involved in conducting networking experiments.

The [paper](https://dl.acm.org/doi/abs/10.1145/3404868.3406670) introducing
NeST was accepted at [ANRW'20](https://irtf.org/anrw/2020/).

`NeST` source code repository is maintained at [GitLab](https://gitlab.com/nitk-nest/nest).

**NOTE**: NeST is currently in beta stage.

## Installation

Instructions to install `NeST` can be found in
[install.rst](https://gitlab.com/nitk-nest/nest/-/blob/master/docs/source/user/install.rst).

## Examples

Several examples, that explain the basic APIs and features of NeST, are
available in the [examples directory](https://gitlab.com/nitk-nest/nest/-/tree/master/examples).

## Documentation

The documentation of NeST APIs can be read online at:
[https://nest.nitk.ac.in/docs/](https://nest.nitk.ac.in/docs/)

Instructions for generating/building the API documentation can be found in
[docs/README.md](https://gitlab.com/nitk-nest/nest/-/blob/master/docs/README.md) folder.

## Unit tests

Tests can be found in `nest/tests` folder.
Run the below command in the repo's root folder to run the tests.

```shell
sudo python3 -m unittest -v
```

**NOTE**: NeST requires **root** access currently to create and manage network namespaces.

## Contributing

To contribute, read [CONTRIBUTING.md](https://gitlab.com/nitk-nest/nest/-/blob/master/CONTRIBUTING.md)
