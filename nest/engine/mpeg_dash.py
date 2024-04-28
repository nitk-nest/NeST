# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2024 NITK Surathkal

"""MPEG DASH commands"""

import os
import tempfile
from .exec import exec_exp_commands, exec_subprocess_in_background


def run_mpeg_dash_http_server(ns_name, port, encoded_chunks_path):
    """
    Run MPEG DASH HTTP server on provided namespace

    Parameters
    ----------
    ns_name : str
        Name of the server namespace
    port: int
        Port number to run the server on.
    encoded_chunks_path : Path
        The path where the encoded chunks are present.

    Returns
    -------
    int
        return code of the command executed
    """

    path_to_server_code = (
        os.path.realpath(os.path.dirname(__file__)) + "/http_server.py"
    )

    cmd_string = f"""ip netns exec {ns_name} \
        python3 {path_to_server_code} {port} {str(encoded_chunks_path)}"""

    return exec_subprocess_in_background(cmd_string)


# pylint: disable=too-many-arguments
def run_mpeg_dash_client(
    ns_name,
    destination_ip,
    port,
    duration,
    out,
    err,
    player,
    enable_audio_playback,
    additional_player_options,
):
    """
    Run MPEG DASH client

    Parameters
    ----------
    ns_name : str
        Name of the client namespace
    destination_ip : str
        IP address of the server namespace
    port : int
        port number of the server at which the MPEG-DASH application is running
    duration :
        Number of seconds for which experiment has to be run
    player: str, optional
        The media player to be used.
    enable_audio_playback: bool
        Enable/disable audio playback
    additional_player_options : string
        User specified options for the video player

    Returns
    -------
    int
        return code of the command executed
    """

    # Obtaining the current linux user's UID
    # in order to configure the PulseAudio sound server
    # to work in a network namespace.

    # pylint: disable=consider-using-with
    try:
        # If sudo has been invoked then the following statements are executed.
        temp_file = tempfile.TemporaryFile()
        # $SUDO_UID is the user ID of the user who invoked sudo
        exec_exp_commands("bash -c 'echo $SUDO_UID' ", stdout=temp_file)
        temp_file.seek(0)
        u_id = int(temp_file.read().decode())
        vlc_binary_prefix = "vlc-wrapper"
    except ValueError:
        # If sudo has not been invoked then the following statements are executed.
        temp_file = tempfile.TemporaryFile()
        exec_exp_commands("bash -c 'echo $UID' ", stdout=temp_file)
        temp_file.seek(0)
        u_id = int(temp_file.read().decode())
        vlc_binary_prefix = "sed -i 's/geteuid/getppid/' /usr/bin/vlc; vlc"

    # Running the media player to stream MPEG-DASH video
    # and setting the quality adaptation logic based on the bandwidth.

    if player == "vlc":
        audio_playback_flag_str = "--no-audio" if not enable_audio_playback else ""

        cmd_string = f"""ip netns exec \
        {ns_name} \
        env PULSE_SERVER=/run/user/{u_id}/pulse/native \
            PULSE_COOKIE=/run/user/{u_id}/pulse/cookie \
        bash -c " \
        {vlc_binary_prefix} \
        http://{destination_ip}:{port}/manifest.mpd \
        --adaptive-logic=rate \
        --loop \
        {audio_playback_flag_str} \
        {additional_player_options}"
        """

    if player == "gpac":
        audio_playback_filter_str = "aout" if enable_audio_playback else ""

        cmd_string = f"""ip netns exec \
        {ns_name} \
        env PULSE_SERVER=/run/user/{u_id}/pulse/native \
            PULSE_COOKIE=/run/user/{u_id}/pulse/cookie \
        bash -c "rm /tmp/gpac_cache -rf; \
        gpac -i \
        http://{destination_ip}:{port}/manifest.mpd"""
        cmd_string += f""":gpac:algo=grate:start_with=min_bw:debug_as=0,1 \
        vout:buffer=1000:mbuffer=5000:cache=none \
        {audio_playback_filter_str} \
        -logs=all@info:ncl \
        -clean-cache \
        -sloop \
        {additional_player_options}"
        """

    return exec_exp_commands(
        cmd_string,
        stdout=out,
        stderr=err,
        timeout=duration,
    )
