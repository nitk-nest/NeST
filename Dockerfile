# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2026 NITK Surathkal

# Main CI Dockerfile
# Relies on the pre-compiled ci-base image to skip unnecessary repeated
# compilation and builds, etc.

ARG BASE_IMAGE_TAG=master
ARG REGISTRY_WITH_IMAGE=registry.gitlab.com/nitk-nest/nest/base
FROM ${REGISTRY_WITH_IMAGE}:${BASE_IMAGE_TAG} AS test

SHELL ["/bin/bash", "-c"]

# Configure FRR
RUN mkdir -p /run/frr && chown frr /run/frr

# -------------------------------------------------------------------
# Dev Stage
# -------------------------------------------------------------------
FROM test AS dev

WORKDIR /home
RUN git clone https://gitlab.com/nitk-nest/nest.git/
WORKDIR /home/nest/
RUN pip install --no-cache-dir .
