# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

""" Constructs CoAP client and sends GET/PUT requests to the server """

# Below implementation is based on the examples from:
# https://aiocoap.readthedocs.io/en/latest/examples.html

import sys
import argparse
import asyncio
import json
import time

import aiocoap


async def get_req(context, uri, mtype, non_timeout):
    """
    Send a GET request to the CoAP server to the given URI

    Parameters
    ----------
    context : aiocoap.Context
        The context object for the client application
    uri : str
        The URI of the resource to which the request is to be made
    mtype : str
        Confirmable(CON) or non-confirmable(NON) message
    non_timeout : int
        Timeout to wait for responses to NON messages
    """
    # Needed to store the output and error data
    out_dict = {}
    err_dict = {}

    # Choosing between confirmable(CON) and non-confirmable(NON) message
    if mtype == "CON":
        # pylint: disable=no-member
        request = aiocoap.Message(code=aiocoap.GET, mtype=aiocoap.Type.CON, uri=uri)
    elif mtype == "NON":
        # pylint: disable=no-member
        request = aiocoap.Message(code=aiocoap.GET, mtype=aiocoap.Type.NON, uri=uri)

    try:
        # Start time for measuring RTT
        rtt_start = time.time()

        # For NON messages, we need a timeout for the response since it is not possible
        # to keep waiting for it. For CON messages, the timeout is set and managed
        # internally in aiocoap so we need not handle it.
        if mtype == "CON":
            # Send request and wait for response
            response = await context.request(request).response
        else:
            # Send request and wait for response or timeout
            response = await asyncio.wait_for(
                context.request(request).response, timeout=non_timeout
            )

        # RTT calculation
        rtt = time.time() - rtt_start

    # Detect asyncio timeout errors for NON messages
    except asyncio.TimeoutError:
        err_dict = {"Error": "Timeout Error", "Exception": str(asyncio.TimeoutError)}
    # Any other misc errors
    # pylint: disable=broad-except
    except Exception as exception:
        err_dict = {"Error": "Failed to fetch resource", "Exception": str(exception)}
    else:
        # Convert raw bytes to the "c.dd" form
        response_code = response.code.dotted

        # Convert the payload in bytes to string
        response_payload_bytes = response.payload
        response_payload = response_payload_bytes.decode("utf-8")

        out_dict = {
            "Response Code": response_code,
            "Response Payload": response_payload,
            "Message Type": mtype,
            "RTT(in secs)": rtt,
        }

    return (out_dict, err_dict)


# pylint: disable=too-many-locals
async def put_req(context, uri, message_payload, mtype, non_timeout):
    """
    Perform a PUT request to the given URI.

    Parameters
    ----------
    context : aiocoap.Context
        The context object for the client application
    uri : str
        The URI of the resource to which the request is to be made
    message_payload : str
        Message payload sent to the server via the PUT request
    mtype : str
        Confirmable(CON) or non-confirmable(NON) message
    non_timeout : int
        Timeout to wait for responses to NON messages
    """
    # Needed to store the output and error data
    out_dict = {}
    err_dict = {}

    payload = message_payload.encode("utf-8")

    # Choosing between confirmable(CON) and non-confirmable(NON) message
    if mtype == "CON":
        # pylint: disable=no-member
        request = aiocoap.Message(
            code=aiocoap.PUT, mtype=aiocoap.Type.CON, payload=payload, uri=uri
        )
    elif mtype == "NON":
        # pylint: disable=no-member
        request = aiocoap.Message(
            code=aiocoap.PUT, mtype=aiocoap.Type.NON, payload=payload, uri=uri
        )

    try:
        # Start time for measuring RTT
        rtt_start = time.time()

        # For NON messages, we need a timeout for the response since it is not possible
        # to keep waiting for it. For CON messages, the timeout is set and managed
        # internally in aiocoap so we need not handle it.
        if mtype == "CON":
            # Send request and wait for response
            response = await context.request(request).response
        else:
            # Send request and wait for response or timeout
            response = await asyncio.wait_for(
                context.request(request).response, timeout=non_timeout
            )

        # RTT calculation
        rtt = time.time() - rtt_start

    # Detect asyncio timeout errors for NON messages
    except asyncio.TimeoutError:
        err_dict = {"Error": "Timeout Error", "Exception": str(asyncio.TimeoutError)}
    # Any other misc errors
    # pylint: disable=broad-except
    except Exception as exception:
        err_dict = {"Error": "Failed to fetch resource", "Exception": str(exception)}
    else:
        # Convert raw bytes to the "c.dd" form
        response_code = response.code.dotted

        # Convert the payload in bytes to string
        response_payload_bytes = response.payload
        response_payload = response_payload_bytes.decode("utf-8")

        out_dict = {
            "Response Code": response_code,
            "Response Payload": response_payload,
            "Message Type": mtype,
            "RTT(in secs)": rtt,
        }

    return (out_dict, err_dict)


# pylint: disable=too-many-locals
async def main():
    """
    Parses client request parameters and generates appropriate traffic
    """

    help_description = "CoAP Client Application"

    # Initialize parser
    parser = argparse.ArgumentParser(description=help_description)

    # Adding arguments for client request
    parser.add_argument("-r", "--request_type", type=str, choices=["put", "get"])
    parser.add_argument("-m", "--message_payload", type=str)
    parser.add_argument("-d", "--destination_ip", type=str)
    parser.add_argument("-c", "--n_con_msgs", type=str)
    parser.add_argument("-n", "--n_non_msgs", type=str)
    parser.add_argument("-t", "--non_timeout", type=str)

    # Read Arguments
    args = parser.parse_args()

    # Constructing the URI from the destination IP
    uri = "coap://" + args.destination_ip + "/sample-resource"

    # Create client context
    context = await aiocoap.Context.create_client_context()

    # Lists for storing outputs and errors for every packet sent
    outputs = []
    errors = []

    total_msgs = int(args.n_non_msgs) + int(args.n_con_msgs)

    # List of coroutine to pass to `gather` for concurrent execution
    coroutine_list = []

    # Parse arguments
    for i in range(0, total_msgs):
        if i < int(args.n_non_msgs):
            mtype = "NON"
        else:
            mtype = "CON"

        # Add GET and PUT request coroutines to the coroutine list
        if args.request_type == "get":
            coroutine_list.append(get_req(context, uri, mtype, float(args.non_timeout)))
        else:
            coroutine_list.append(
                put_req(
                    context, uri, args.message_payload, mtype, float(args.non_timeout)
                )
            )

    # Start time for measuring Flow Completion Time(FCT)
    fct_start = time.time()

    # Run all the coroutines
    results = await asyncio.gather(*coroutine_list)

    # Calculate FCT
    # This includes NON messages as well since they can receive responses as well
    fct = time.time() - fct_start

    # Add the FCT to the outputs dictionary
    outputs.append({"Flow Completion Time(in secs)": fct})

    # Split the final results into outputs and errors
    for i in results:
        (output, error) = i
        outputs.append(output)
        errors.append(error)

    # Convert the output and error lists into JSON format
    outputs_json = json.dumps(outputs)
    errors_json = json.dumps(errors)

    # Print outputs and errors into respective streams
    print(outputs_json, file=sys.stdout)
    print(errors_json, file=sys.stderr)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
