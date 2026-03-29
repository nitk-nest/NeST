# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2026 NITK Surathkal

# Use sign-off regex from valid_signoff
from valid_signoff import NAME_EMAIL_REGEX
from gitlint.rules import CommitRule, RuleViolation
from gitlint.options import IntOption
import re


class CustomBodyLength(CommitRule):
    """
    This rule enforces a maximum body line length (like `body-max-line-length`) but ignores sign-off/co-author lines.
    """

    name = "custom-body-max-line-length"
    # User-defined Commit-rule 2
    id = "UC2"

    options_spec = [
        IntOption(
            "line-length",  # name
            80,  # default value
            "Maximum allowed line length in the commit message body, ignoring sign-offs.",  # description
        )
    ]

    def validate(self, commit):
        violations = []
        max_line_length = self.options["line-length"].value

        for line_num, line in enumerate(commit.message.body):
            # Skip length check, if line matches sign-off regex
            if re.fullmatch(NAME_EMAIL_REGEX, line):
                continue

            if len(line) > max_line_length:
                violation_line_num = line_num + 2
                msg = f"Body line is too long ({len(line)} > {max_line_length} characters)"
                violations.append(RuleViolation(self.id, msg, line, violation_line_num))

        return violations
