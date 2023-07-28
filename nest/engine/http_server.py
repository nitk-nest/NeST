# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2024 NITK Surathkal

"""Custom HTTP Server"""
import http.server
import sys
import os


class CustomHttpHandler(http.server.SimpleHTTPRequestHandler):
    """
    CustomHTTPHandler that enables the server to serve a particular
    directory and also use HTTP/1.1 protocol.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=sys.argv[2], **kwargs)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)

    PORT = int(sys.argv[1])
    PATH = sys.argv[2]

    if not os.path.exists(PATH):
        sys.exit(1)

    http.server.test(
        HandlerClass=CustomHttpHandler,
        protocol="HTTP/1.1",
        port=PORT,
    )
