# Installation

**NOTE**: `NeST` is supported for Linux systems only.

## Install dependencies

1. Ensure iproute2 suite is installed with your kernel

    ```shell
    $ ip -V
    ip utility, iproute2-ss200127
    ```

2. Ensure ping is installed

    ```shell
    $ ping -V
    ping from iputils s20190709
    ```

3. Install netperf  
    You can check if netperf is installed by running the command:

    ```shell
    $ netperf -V
    Netperf version 2.7.0
    ```

    If netperf is not installed, then it can be obtained from your Linux distribution packages.
    For Ubuntu run:

    ```shell
    sudo apt install netperf
    ```

4. Install iperf3  
    You can check if iperf is installed by running the command:

    ```shell
    $ iperf3 -v
    iperf 3.7 (cJSON 1.5.2)
    Linux your-system 5.4.0-51-generic #56-Ubuntu SMP Mon Oct 5 14:28:49 UTC  2020 x86_64
    ```

    If iperf3 is not installed, then it can be obtained from your Linux distribution packages.
    For Ubuntu run:

    ```shell
    sudo apt install iperf3
    ```

5. Install and setup quagga  
    To install quagga on Ubuntu run

    ```shell
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

```shell
pip3 install nitk-nest
```

**NOTE**: If you install NeST inside a virtual environment or in your "user" home directory,
then you can run python scripts using NeST as follows:

```shell
sudo -E python3 <program.py>
```

Note that NeST requires **root** access currently to create and manage network namespaces.

### 2. From source

1. Clone the repository

    ```shell
    git clone https://gitlab.com/nitk-nest/nest.git
    ```

2. Install via pip

    If you are developing, then it is better to do it in editable mode.
    In editable mode, your code changes are instantly propagated to the
    library code without reinstalling.

    ```shell
    python -m pip install -e .
    ```

    If you are not developing, then run the below command:

    ```shell
    python -m pip install .
    ```
