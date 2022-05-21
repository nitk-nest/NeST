# Examples to demonstrate the usage of config options in NeST

This directory contains the following examples to understand how config
options can be used in `NeST`. These options provide flexibility to the NeST
users to customize the parameters used in the experiment. We recommend that
you walk through these examples in the same order as they are presented.

## 1. config-1-point-to-point-1.py
This program emulates a point to point network between two hosts `h1` and
`h2`. Five ping packets are sent from `h1` to `h2`, and the success/failure
of these packets is reported. It is similar to `point-to-point-1.py` in
`examples/basic-examples`. This program shows two `config` options in NeST
for ease of experimentation. For this purpose, a new package called `config`
is imported in this program.

By default, NeST deletes all the nodes (or network namespaces) at the end of
the experiment. One of the `config` options in NeST allows the user to
customize this behavior, if needed, and retain the namespaces. Another `config`
option in NeST is to avoid giving random names to the namespaces. Since NeST
allows multiple programs to run in parallel on the same machine, it internally
assigns random names to the namespaces by default. However, when random names
are disabled, node names cannot be longer than three characters. We use names
`h1` and `h2` in this example.

**IMPORTANT NOTE**  
Do not forget to delete the namespaces manually before re-running this program.
You can delete namespaces one-by-one by using `sudo ip netns del h1` command
(similarly for `h2`) or delete all namespaces at once by using
`sudo ip --all netns del`. Be careful if you choose to delete all namespaces
because this command will delete all the namespaces in your system (even the
ones that were not created by NeST).

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: config-1-point-to-point-1.py -->

## 2. config-2-point-to-point-1.py
This program emulates a point to point network between two hosts `h1` and
`h2`. Five ping packets are sent from `h1` to `h2`, and the success/failure
of these packets is reported. It is similar to `point-to-point-1.py` in
`examples/basic-examples`. This program shows a `config` option in NeST for
the purpose of logging. Note: we have imported a new package called `config`
in this program.

NeST supports different levels of logging by using Python's logging levels.
By default, the logging is enabled at `INFO` level. Other levels supported are:
`NOTSET`, `TRACE`, `DEBUG`, `WARNING`, `ERROR` and `CRITICAL`.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: config-2-point-to-point-1.py -->

## 3. config-3-point-to-point-1.py
This program emulates a point to point network between two hosts `h1` and
`h2`. Five ping packets are sent from `h1` to `h2`, and the success/failure
of these packets is reported. It is similar to `point-to-point-1.py` in
`examples/basic-examples`. This program shows a `config` option in NeST to
import custom configuration from a JSON file. This option overwrites the
default values in NeST for the parameters that are specified in the JSON file.
The default values of other parameters are not overwritten. Note: we have
imported a new package called `config` in this program.

This program uses the `config` option to read the configuration from the file
named `custom-config.json` which is placed in the current directory. If the
JSON file is named as `nest-config.json` and placed in the same directory as
this program, or in /etc or ~/, then this program does not need to use the
`config` option. It directly reads the configuration from `nest-config.json`.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: config-3-point-to-point-1.py -->

## 4. config-4-point-to-point-1.py
This program emulates a point to point network between two hosts `h1` and
`h2`. Five ping packets are sent from `h1` to `h2`, and the success/failure
of these packets is reported. It is similar to `config-2-point-to-point-1.py`
example. This program shows a `config` option for the purpose of tracing
internal Linux commands (for example, those of iproute2) executed by NeST.
Note: we have imported a new package called `config` in this program.

NeST supports different levels of logging by using Python's logging levels.
By default, the logging is enabled at INFO level. Other levels supported are:
NOTSET, TRACE, DEBUG, WARNING, ERROR and CRITICAL. This program enables the
TRACE level log, which creates a file called `commands.sh` with all the
`iproute2` commands NeST internally executes. But by default, NeST assigns
random names to the network namespaces. Hence, when TRACE level log is enabled,
the names of network namespaces visible in `commands.sh` would be random, and
not user-friendly. To make the names look user-friendly, random name assignment
is disbaled in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: config-4-point-to-point-1.py -->

The details of all `config` options supported in NeST are available [here](http://nest.nitk.ac.in/docs/master/user/config.html).
