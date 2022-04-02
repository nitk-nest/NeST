# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

""" Sets up a CoAP server with a sample resource """

# Below implementation is based on the examples from:
# https://aiocoap.readthedocs.io/en/latest/examples.html

import argparse
import asyncio

from aiocoap import resource
import aiocoap


class SampleResource(resource.Resource):
    """
    Represents the resource stored on the server.
    Supports GET and PUT requests.

    Attributes
    ----------
    content : bytes
        represents the content stored on the server as bytes
    """

    def __init__(self, content: str):
        """
        Constructor to initialize the resource.

        Parameters
        ----------
        content : str
            content to initialize the resource with
        """
        # pylint: disable=non-parent-init-called
        super().__init__()
        self.set_content(content.encode("utf-8"))

    def set_content(self, content: bytes):
        """
        Set content for the resource. Encoded into
        bytes before setting.

        Parameters
        ----------
        content : bytes
            content to set for the resource
        """
        self.content = content

    # pylint: disable=unused-argument
    async def render_get(self, request):
        """
        Handler for GET requests received for the resource

        Parameters
        ----------
        request : aiocoap.Message
            GET request received from the client

        Returns
        -------
        aiocoap.Message
            response message for the GET request
        """
        return aiocoap.Message(payload=self.content)

    async def render_put(self, request):
        """
        Handler for PUT requests received for the resource

        Parameters
        ----------
        request : aiocoap.Message
            PUT request received from the client

        Returns
        -------
        aiocoap.Message
            response message for the PUT request
        """
        self.set_content(request.payload)
        # pylint: disable=no-member
        return aiocoap.Message(code=aiocoap.CHANGED, payload=self.content)


def main():
    """
    Parses the content for the server resource, sets up the
    root element, adds the resource to the root element, creates
    the server context and then runs the server process.
    """

    help_description = "CoAP server"

    # Initialize parser
    parser = argparse.ArgumentParser(description=help_description)

    # Adding arguments for client request
    parser.add_argument("-c", "--content", type=str)

    # Read Arguments
    args = parser.parse_args()

    # Resource tree creation, starting with the root element
    root_element = resource.Site()

    # For defining the entry point for requesting the list of links
    # for resources stored in the server. This is for performing
    # CoRE(Constrained RESTful Environments) Resource Discovery.
    root_element.add_resource(
        [".well-known", "core"],
        resource.WKCResource(root_element.get_resources_as_linkheader),
    )

    # Adding the SampleResource defined in this file
    root_element.add_resource(["sample-resource"], SampleResource(args.content))

    # Creating the server context
    asyncio.Task(aiocoap.Context.create_server_context(root_element))

    # This is a message for the parent process to consider this
    # background subprocess to have successfully run and to return an
    # exit code of 0
    print("Process successful\n")

    # Running the server
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
