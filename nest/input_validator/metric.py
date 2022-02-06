# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""
Contains classes for validation for commonly used
metrics in NeST. For eg., Bandwidth and Delay
"""

import re
from .input_validator import input_validator


class Metric:
    """
    Base type for metrics. Metrics are of the format <value><unit>.

    For eg., `Bandwidth` type ("10mbit") derives from this class. Here,
    value="10" and unit="mbit"
    """

    valid_units = []

    @input_validator
    def __init__(
        self, metric: str, value_regex=r"[0-9]+(\.[0-9]+)?", unit_regex=r"[A-Za-z]+"
    ):
        """
        Constructor for Metric. Validates if `metric` is in <value><unit>
        format.

        Parameters
        ----------
        metric: str
            Value of the metric
        """
        if not re.fullmatch(value_regex + unit_regex, metric):
            raise ValueError(
                f"{metric} is not a valid metric. Metrics must be of the format "
                f"<value><unit>"
            )

        # Extract value and unit
        self._value = re.search(value_regex, metric).group()
        self._unit = re.search(unit_regex, metric).group()

        self._string_value = metric

    @property
    def value(self):
        """
        Get the value of the metric (without unit)
        """
        return self._value

    @property
    def unit(self):
        """
        Get the unit of the metric
        """
        return self._unit

    @property
    def string_value(self):
        """
        Get string value of the mrtic
        """
        return self._string_value

    @staticmethod
    def allowed_type_cast():
        """
        Indicate str can be typecasted into Metric type
        """
        return [str]


class Bandwidth(Metric):
    """
    Validates that the bandwidth is in expected format.
    """

    # fmt: off

    valid_units = [
        "bit", "kbit", "kibit", "mbit", "mibit", "gbit", "gibit", "tbit", "tibit",
        "bps", "kbps", "kibps", "mbps", "mibps", "gbps", "gibps", "tbps", "tibps",
    ]

    # fmt: on

    def __init__(self, bandwidth: str):
        """
        Parameters
        ----------
        bandwidth: str
            The value of bandwidth
        """
        super().__init__(bandwidth)

        if self.unit not in Bandwidth.valid_units:
            raise ValueError(f"{self.unit} is not a valid unit for bandwidth.")


class Delay(Metric):
    """
    Validates that the delay is in expected format.
    """

    valid_units = ["s", "sec", "secs", "ms", "msec", "msecs", "us", "usec", "usecs"]

    def __init__(self, delay: str):
        """
        Parameters
        ----------
        delay: str
            The value of delay
        """
        super().__init__(delay)

        if self.unit not in Delay.valid_units:
            raise ValueError(f"{self.unit} is not a valid unit for delay.")


class Percentage(Metric):
    """
    Validates that the percentage is in expected format.
    """

    def __init__(self, percentage: str):
        """
        Parameters
        ----------
        percentage: str
            The value of percentage
        """
        super().__init__(percentage, unit_regex=r"%")

        if not 0 <= float(self.value) <= 100:
            raise ValueError(f"{self.string_value} is not a valid percentage.")
