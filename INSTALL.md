# Installation

**NOTE**: `NeST` is supported for Linux systems only.

## Install dependencies

1. Ensure iproute2 suite is installed with your kernel
    ```
    $ ip -V
    ip utility, iproute2-ss200127
    ```

1. Ensure ping is installed
    ```
    $ ping -V
    ping from iputils s20190709
    ```

2. Install netperf  
    You can check if netperf is installed by running the command:
    ```
    $ netperf -V
    Netperf version 2.7.0
    ```
    If netperf is not installed, then it can be obtained from your linux distribution packages.
    For ubuntu run:
    ```
    $ sudo apt install netperf
    ```
3. Install iperf3  
    You can check if iperf is installed by running the command:
    ```
    $ iperf3 -v
    iperf 3.7 (cJSON 1.5.2)
    Linux your-system 5.4.0-51-generic #56-Ubuntu SMP Mon Oct 5 14:28:49 UTC  2020 x86_64
    ```
    If iperf3 is not installed, then it can be obtained from your linux distribution packages.
    For ubuntu run:
    ```
    $ sudo apt install iperf3
    ```

4. Install and setup quagga  
    To install quagga on ubuntu run
    ```
    sudo apt install quagga quagga-doc
    ```

    Edit `/etc/quagga/daemons` with an editor using sudo and turn on zebra, ripd and ospf by changing the following lines
    ```
    zebra=no -> zebra=yes
    ripd=no -> ripd=yes
    ospfd=no -> ospfd=yes
    ```
    If the `daemons` file doesn't exist create one and add the following lines to the file
    ```
    zebra=yes
    bgpd=no
    ospfd=yes
    ospf6d=no
    ripd=yes
    ripngd=no
    isisd=no
    babeld=no
    ```
   **Note**: Ensure that a quagga owned directory named 'quagga'   exists under `/run`

## Installing NeST
### 1. From PyPi
Install from the [Python Package Index](https://pypi.org/project/nitk-nest/)

```
pip3 install nitk-nest
```

### 2. From source

1. Clone the repository
    ```
    git clone https://gitlab.com/wing-nitk/linux-networking/nest.git
    ```

2. Install via pip

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
