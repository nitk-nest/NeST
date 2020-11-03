# NeST: Network Stack Tester

`NeST` is a python3 package that handles testbed setup, testbed configuration,
collecting and visualizing data by providing a user friendly API, addressing
common issues involved in conducting networking experiments.

`NeST` source code repository is maintained at [GitLab](https://gitlab.com/nitk-nest/nest).

## Installation
To install NeST from the [Python Package Index](https://pypi.org/project/nitk-nest) run
```
pip install nitk-nest
```
Instructions to install `NeST` from source can be found in
[INSTALL.md](https://gitlab.com/nitk-nest/nest/-/blob/master/INSTALL.md).

## Documentation
Instructions for generating/building the API documentation can be found in
[docs/README.md](https://gitlab.com/nitk-nest/nest/-/blob/master/docs/README.md) folder.

The formatted documentation can also be read at:
[https://nitk-nest.github.io/docs/](https://nitk-nest.github.io/docs/)

## Unit tests
Tests can be found in `nest/tests` folder.\
Run the below command in the repo's root folder to run the tests.
```
sudo python -m unittest -v
```

**NOTE**: If tests are run from within a virtual environment, then an additional
`-E` might be needed for `sudo`
```
sudo -E python -m unittest
```

## Contributing

To contibute, read [CONTRIBUTING.md](https://gitlab.com/nitk-nest/nest/-/blob/master/CONTRIBUTING.md)

**NOTE**: Running a script that uses NeST requires root access.
