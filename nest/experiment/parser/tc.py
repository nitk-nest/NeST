# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
Runs tc command and parses qdisc stats
from its output
"""

import re
import json
import os
from functools import partial
from time import strptime, strftime
from nest.experiment.interrupts import handle_keyboard_interrupt
from .runnerbase import Runner
from ..results import TcResults
from ...topology_map import TopologyMap
from ...engine.tc import get_tc_version
from ...engine.iterators import run_tc


class TcRunner(Runner):
    """
    Runs tc command and stores and parses the output

    Attributes
    ----------
    iterator : str
        absolute path of the tc iterator script
    old_kernel_version : str
        minimum kernel version required
    new_kernel_version : str
        kernel version from which tc has concrete JSON support
    ns_id : str
        network namespace to run tc from
    dev : str
        dev id to collect tc stats from
    run_time : num
        total time to run tc for
    """

    iterator = os.path.realpath(os.path.dirname(__file__)) + "/iterators/tc.sh"

    # tc versions are in date formatted
    # TODO: move these to a config file

    # NOTE: Both the below versions are in OLD tc version format
    # Refer docstring of `check_tc_version_format`

    # Minimum version of tc required by NeST
    MINIMUM_SUPPORTED_VERSION = strptime("20180129", "%Y%m%d")

    # tc version with good JSON support for displaying stats
    JSON_SUPPORTED_VERSION = strptime("20190319", "%Y%m%d")

    # Qdiscs supported prior to good JSON support in tc
    PRIOR_JSON_QDISCS_SUPPORTED = ["codel", "fq_codel", "pie"]

    def __init__(self, ns_id, dev, qdisc, run_time):
        """
        Constructor to initialize tc runner

        Parameters
        ----------
        ns_id : str
            network namespace to run tc from
        dev : str
            dev id to collect tc stats from
        qdisc : str
            qdisc name [eg. 'codel', 'pie']
        run_time : num
            total time to run tc for
        """
        self.dev = dev
        self.qdisc = qdisc

        # Start parsing from 0s
        super().__init__(ns_id, 0, run_time)

        # Tc version check
        self.version_check()

    def version_check(self):
        """
        Check the tc version and throw exception if any
        unsupported task is requested from NeST
        """
        tc_version_format = self.check_tc_version_format()

        if tc_version_format == "old_version_format":
            cur_tc_version = self.parsed_tc_version()

            if cur_tc_version < TcRunner.MINIMUM_SUPPORTED_VERSION:
                # TODO: Not sure if it's the right exception to raise
                version = "iproute2-ss" + strftime(
                    "%y%m%d", TcRunner.MINIMUM_SUPPORTED_VERSION
                )
                raise Exception(
                    f"NeST does not support qdisc parsing for tc version below "
                    f"{version}"
                )

            if cur_tc_version < TcRunner.JSON_SUPPORTED_VERSION:
                if self.qdisc not in TcRunner.PRIOR_JSON_QDISCS_SUPPORTED:

                    version = "iproute2-ss" + strftime(
                        "%y%m%d", TcRunner.JSON_SUPPORTED_VERSION
                    )
                    raise Exception(
                        f"NeST does not support {self.qdisc} qdisc parsing for tc "
                        f"version below {version}. Supported "
                        f"qdiscs are {TcRunner.PRIOR_JSON_QDISCS_SUPPORTED}"
                    )

    def run(self):
        """
        Runs the tc iterator
        """
        super().run(
            partial(run_tc, self.ns_id, TcRunner.iterator, self.dev, self.run_time),
            error_string_prefix="Collecting qdisc stats",
        )

    def get_qdisc_specific_params(self):
        """
        Parameters to be obtained for a specific qdisc

        Returns
        -------
        dict:
            qdisc keyed list of parameters to parsed
        """
        qdisc_param = {
            "codel": ["count", "lastcount", "ldelay", "drop_next"],
            "fq_codel": ["maxpacket", "drop_overlimit", "new_flow_count"],
            "pie": ["prob", "delay", "avg_dq_rate"],
        }
        return qdisc_param

    def get_qdisc_re(self):
        """
        Compile regular expression for parsing qdisc specific parameters

        Returns
        -------
        dict
            qdisc keyed regular expression
        """
        qdisc_re = {}
        qdisc_re["codel"] = re.compile(
            r"count (?P<count>\d+) "
            r"lastcount (?P<lastcount>\d+) "
            r"ldelay (?P<ldelay>[0-9\.]+[mu]?s) "
            r"(?P<dropping>dropping)? ?"
            r"drop_next (?P<drop_next>-?[0-9\.]+[mu]?s)"
        )
        qdisc_re["fq_codel"] = re.compile(
            r"maxpacket (?P<maxpacket>\d+) "
            r"drop_overlimit (?P<drop_overlimit>\d+) "
            r"new_flow_count (?P<new_flow_count>\d+) "
        )
        qdisc_re["pie"] = re.compile(
            r"prob (?P<prob>[0-9\.]+) "
            r"delay (?P<delay>[0-9\.]+[mu]?s) "
            r"avg_dq_rate (?P<avg_dq_rate>\d+)"
        )
        return qdisc_re

    def repl(self, match):
        """
        Called by re.sub() for every match

        Parameters
        ----------
        match : Match
            Match object captured by the pattern

        Returns
        -------
        str
            string to replace the matched string
        """
        if match.group(1):
            if match.group(1).endswith(","):
                value = repr(match.group(1))
                return f':"{value}",'

            value = repr(match.group(1))
            return f':"{value}"'
        return ""

    def clean_json(self, stats):
        """
        JSON formatted tc stats with invalid JSON keys
        and values are removed or fixed

        Parameters
        ----------
        stats : str
            unclean json formatted stats

        Returns
        -------
        str
            fixed json stats
        """
        # pattern to remove the options key
        options_pattern = r'"options":(\s)*{(.|\n)*?},'
        stats = re.sub(options_pattern, "", stats)

        # pattern to enclose all the values with " "
        value_pattern = r":(\s(\w|\s|\n|\.)+,?)"
        stats = re.sub(value_pattern, self.repl, stats)
        return stats

    def parsing_helper_before_good_json_support(self, raw_stats, qdisc_param, qdisc_re):
        """
        Parsing tc command on Linux kernel versions
        4.15.0 to 5.4

        Parameters
        ----------
        raw_stats : list(str)
            list of stats collected at each iteration
        qdisc_param : dict
            parameters to be obtained for a specific qdisc
        qdisc_re : dict
            regular expression for parsing qdisc specific parameters

        Returns
        -------
        dict
            handle keyed dict with list of stats
        """

        aggregate_stats = {}

        for raw_stat in raw_stats[:-1]:
            timestamp_pattern = r"timestamp:(?P<timestamp>\d+\.\d+)"
            timestamp = re.search(timestamp_pattern, raw_stat).group("timestamp")
            raw_stat = re.sub(timestamp_pattern, "", raw_stat)
            raw_stat = json.loads(self.clean_json(raw_stat))
            stats_dict = {}
            for qdisc_stat in raw_stat:
                qdisc = qdisc_stat["kind"]
                if (
                    qdisc in TcRunner.PRIOR_JSON_QDISCS_SUPPORTED
                    and qdisc == self.qdisc
                ):
                    handle = qdisc_stat["handle"]
                    if handle not in aggregate_stats:
                        aggregate_stats[handle] = []
                    qdisc_stat = qdisc_stat["qlen"]
                    search_obj = qdisc_re[qdisc].search(qdisc_stat)
                    stats_dict["timestamp"] = str(timestamp)
                    stats_dict["kind"] = qdisc
                    for param in qdisc_param[qdisc]:
                        stats_dict[param] = search_obj.group(param)
                    aggregate_stats[handle].append(stats_dict)
        return aggregate_stats

    def parsing_helper(self, raw_stats):
        """
        Parsing tc command on Linux kernel version
        5.5 and above

        Parameters
        ----------
        raw_stats : list(str)
            list of stats collected at each iteration

        Returns
        -------
        dict
            handle keyed dict with list of stats
        """
        aggregate_stats = {}
        for raw_stat in raw_stats[:-1]:
            timestamp_pattern = r"timestamp:(?P<timestamp>\d+\.\d+)"
            timestamp = re.search(timestamp_pattern, raw_stat).group("timestamp")
            raw_stat = re.sub(timestamp_pattern, "", raw_stat)
            raw_stat = json.loads(raw_stat)
            stats_dict = {}
            for qdisc_stat in raw_stat:
                qdisc = qdisc_stat["kind"]
                if qdisc == self.qdisc:  # To ignore the HTB qdisc
                    handle = qdisc_stat["handle"]
                    if handle not in aggregate_stats:
                        aggregate_stats[handle] = []

                    stats_dict["timestamp"] = str(timestamp)
                    stats_dict.update(qdisc_stat)
                    stats_dict.pop("handle", None)
                    stats_dict.pop("options", None)
                    stats_dict.pop("parent", None)

                    aggregate_stats[handle].append(stats_dict)
        return aggregate_stats

    def check_tc_version_format(self):
        """
        iproute2 changed its versioning format after v5.8.0

        For example, below are the output of `tc -V` for versions near
        v5.8.0 (this list was compiled by checking the iproute2 git repository):

        main   - tc utility, iproute2-5.8.0
        v5.8.0 - tc utility, iproute2-v5.7.0-77-gb687d1067169
        v5.7.0 - tc utility, iproute2-ss200602
        v5.6.0 - tc utility, iproute2-ss200330

        So the function will return 'new_version_format' for versions
        after v5.7.0, else the function will return 'old_version_format'
        """
        old_version_format = "tc utility, iproute2-ss[0-9]{6}\n"
        tc_version = get_tc_version()

        if re.search(old_version_format, tc_version):
            return "old_version_format"

        return "new_version_format"

    def parsed_tc_version(self):
        """
        [For OLD tc format, refer docstring of `check_tc_version_format`]

        Parses the current tc version

        Returns
        -------
        struct_time
            current tc version as date
        """
        cur_tc_version = get_tc_version()
        # pylint: disable=use-maxsplit-arg
        cur_tc_version = "20" + cur_tc_version.split(" ")[-1][-7:].strip()
        return strptime(cur_tc_version, "%Y%m%d")

    @handle_keyboard_interrupt
    def parse(self):
        """
        Parses the required data from tc-qdisc output
        """

        self.out.seek(0)  # rewind to start of the temp file

        # See `iterators/tc.sh` for output format
        raw_stats = self.out.read().decode().split("---")
        aggregate_stats = {}

        tc_version_format = self.check_tc_version_format()

        if tc_version_format == "new_version_format":
            aggregate_stats = self.parsing_helper(raw_stats)

        elif tc_version_format == "old_version_format":
            cur_tc_version = self.parsed_tc_version()

            # tc produces different JSON output format
            # based on the version
            if cur_tc_version >= TcRunner.JSON_SUPPORTED_VERSION:
                aggregate_stats = self.parsing_helper(raw_stats)

            elif cur_tc_version >= TcRunner.MINIMUM_SUPPORTED_VERSION:
                qdisc_param = self.get_qdisc_specific_params()
                qdisc_re = self.get_qdisc_re()
                aggregate_stats = self.parsing_helper_before_good_json_support(
                    raw_stats, qdisc_param, qdisc_re
                )

        # Store parsed results
        dev_name = TopologyMap.get_device(self.ns_id, self.dev).name
        TcResults.add_result(self.ns_id, {dev_name: aggregate_stats})
