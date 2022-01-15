# Utilities

Scripts related to NeST repo maintenance.

## run_examples.py

This program runs all the NeST examples. It is useful in checking that
all NeST examples are in good state and helps in catching in regressions.

This script should be run from NeST root folder as below:
```
$ sudo pytest -o python_files="utils/run_examples.py"
```

Note that `pytest` and `coverage` are dependencies for this program.
