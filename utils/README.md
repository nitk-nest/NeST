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

## gitlint_rules/

This directory contains custom gitlint rules for NeST. Custom rules include:

- [valid_signoff.py](./gitlint_rules/valid_signoff.py)
- [custom_max_line_length.py](./gitlint_rules/custom_max_line_length.py)

All rules here complement the [.gitlint](../.gitlint) commit linter.
Gitlint can be extended for more advanced commit checks, refer the [documentation](https://jorisroovers.com/gitlint/latest/rules/user_defined_rules/).

Gitlint is normally run indirectly, as a part of ci. It can be used to manually check the previous commit as below:
```
$ gitlint -- debug
```

`gitlint`, `gitlint-core` are dependencies for these scripts.

### valid_signoff.py

This rule validates sign-off and co-author lines in a commit.
