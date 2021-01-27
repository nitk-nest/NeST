# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Handle plotting results obtained"""
import matplotlib
from matplotlib import style

# Since plots are not shown in window, use the non-interactive Agg backend.
# Also fixes https://gitlab.com/nitk-nest/nest/-/issues/73
# Many plotting processes were connecting to X-server simultaneously.
# This created errors as X-server couldn't handle requests
matplotlib.use("agg")

# Set plot style
style.use("seaborn-paper")
style.use("ggplot")
