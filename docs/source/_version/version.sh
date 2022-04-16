# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

# Use this file to fix already published versions of docs website.

# Update v0.4 tag, since we want some of the fixes we made
# after tag v0.4 to be part of the website (v0.4 version).
echo "Update v0.4 tag to commit 9cc1880"
git tag -f v0.4 9cc1880a4452c33587924c5b21e8cb339a6e1589
