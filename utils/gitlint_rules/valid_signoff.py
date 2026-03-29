# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2026 NITK Surathkal

from gitlint.rules import CommitRule, RuleViolation
import re

# A sign-off or co-author line ends with email, particularly '>'
NAME_EMAIL_REGEX = r".+\x20<.+@.+>$"


class SignOffValid(CommitRule):
    """
    This rule enforces the commit sign-off or co-author line(s) are valid
    """

    name = "sign-off-is-valid"
    # User-defined Commit-rule 1
    id = "UC1"

    def validate(self, commit):
        violations = []

        for line_num, line in enumerate(commit.message.body):
            # Validation rule
            if re.fullmatch(NAME_EMAIL_REGEX, line) is not None and not (
                line.startswith("Signed-off-by: ")
                or line.startswith("Co-authored-by: ")
            ):
                violation_line_num = line_num + 2
                msg = "Signing was invalid. Please ensure it starts with `Signed-off-by:` or `Co-authored-by:`"
                violations.append(RuleViolation(self.id, msg, line, violation_line_num))
        return violations
