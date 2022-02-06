# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""
This module handles the validation of inputs passed to methods
(mainly for client-side APIs).

All methods which require input validation should be decorated by
`@input_validator`.

For eg., the below method called `samplemethod` is decorated by
`@input_validator`:

    @input_validator
    def samplemethod(arg1: Type1, arg2: Type2):
        ...

When the above method is invoked:

    samplemethod(input1, input2)

The decorator `@input_validator` validates if `input1` is of type
`Type1` and if `input2` is of type `Type2`. Say, `input1` is not
of `Type1`. Then, it will additionally check if `input1` can be
safely typecasted to `Type1`. If even this is not possible, then
the decorator throws an exception.

For figuring out if `input1` can be typecasted to `Type1`, there are
two requirements for the class `Type1`:
  * The class is expected to have a constructor with 1 parameter
    (excluding self). The constructor should raise ValueError if there
    is any error in validation of parameters.
  * The class should have a static method called `allowed_type_cast()`.
    It should return a list of types that can safely be typecasted to
    `Type1`. The logic for typecasting should be handled in the constructor.

If the above two requirements are not met, then `@input_validator` decorator
will not attempt to typecast the input.

NOTE: If a method has more than one decorator, then input_validator should
be applied before all other decorators.

    @some_other_decorator
    @input_validator
    def samplemethod(arg1: Type1, arg2: Type2):
        ...
"""

from .input_validator import input_validator
