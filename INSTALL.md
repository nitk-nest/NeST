# Installation

**NOTE**: `NeST` is supported for Linux systems only.

The following instrcutions are to install `NeST` from source.

#### 1. Ensure that netperf is installed in your system.

You can check if netperf is installed by running the command:
```
$ netperf -V
Netperf version 2.7.0
```

If netperf is not installed, then it can be obtained from your linux
distribution packages.

#### 2. Clone NeST source repository
```
git clone https://gitlab.com/wing-nitk/linux-networking/nest.git
```

#### 3. pip install

If you are developing, then it is better to do it in editable mode.
In editable mode, your code changes are instantly propagated to the
library code without reinstalling.
```
python -m pip install -e .
```

If you are not developing, then run the below command:
```
python -m pip install .
```
