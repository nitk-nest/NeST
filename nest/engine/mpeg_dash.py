# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2026 NITK Surathkal

"""MPEG DASH commands"""

import os
import tempfile
import logging
from .exec import exec_exp_commands, exec_subprocess_in_background


def _is_headless_environment():
    """
    Detect whether the environment is headless (no GUI).
    Docker containers are always treated as headless.

    Returns:
        bool: True if headless, False if display is available
    """
    # Treat Docker as headless, even if DISPLAY is set
    if os.path.exists("/.dockerenv"):
        return True

    # Check for X11 display
    has_x11 = bool(os.environ.get("DISPLAY"))

    # Check for Wayland display
    has_wayland = bool(os.environ.get("WAYLAND_DISPLAY"))

    # If either display system is available, classify it as not headless
    if has_x11 or has_wayland:
        return False

    return True


def _get_user_uid_and_vlc_prefix():
    """
    Obtain UID of the invoking user and appropriate VLC binary prefix.
    Handles sudo and non-sudo invocations.
    """

    def _read_uid(cmd):
        with tempfile.TemporaryFile() as temp_file:
            exec_exp_commands(cmd, stdout=temp_file)
            temp_file.seek(0)
            return int(temp_file.read().decode())

    try:
        # If sudo has been invoked then the following statements are executed.
        # $SUDO_UID is the user ID of the user who invoked sudo
        uid = _read_uid("bash -c 'echo $SUDO_UID'")
        return uid, "vlc-wrapper"
    except ValueError:
        # If sudo has not been invoked then the following statements are executed.
        uid = _read_uid("bash -c 'echo $UID'")
        return (
            uid,
            "sed -i 's/geteuid/getppid/' /usr/bin/vlc; vlc",
        )


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


def _build_vlc_command(
    client_config,
    u_id,
    vlc_binary_prefix,
    is_headless,
    player_config,
):
    """
    Build the VLC command based on the client configuration and environment.

    Parameters
    ----------
    client_config : dict
        Configuration for the client, including namespace, destination IP, and port.
    u_id : int
        UID of the invoking user, used for PulseAudio configuration.
    vlc_binary_prefix : str
        The prefix to use for the VLC binary, which may include modifications for non-sudo usage.
    is_headless : bool
        Whether the environment is headless (no GUI).
    player_config : dict
        Configuration for the player,
        including options for audio/video playback and additional VLC options.
    Returns
    -------
    list
        A list of command parts that can be joined to form the final VLC command.
    """
    ns_name = client_config["ns_name"]
    destination_ip = client_config["destination_ip"]
    port = client_config["port"]
    enable_audio_playback = bool(player_config.get("enable_audio_playback", True))
    enable_video_playback = bool(player_config.get("enable_video_playback", True))
    additional_player_options = player_config.get("additional_player_options", "")
    cmd_parts = [
        f"ip netns exec {ns_name}",
        "env",
        f"PULSE_SERVER=/run/user/{u_id}/pulse/native",
        f"PULSE_COOKIE=/run/user/{u_id}/pulse/cookie",
    ]

    if is_headless or not enable_video_playback:
        cmd_parts.extend(["SDL_VIDEODRIVER=dummy", "SDL_AUDIODRIVER=dummy"])

    cmd_parts.append('bash -c "')

    cmd_parts.extend(
        [
            vlc_binary_prefix,
            f"http://{destination_ip}:{port}/manifest.mpd",
            "--adaptive-logic=rate",
            "--loop",
        ]
    )

    if is_headless or not enable_video_playback:
        cmd_parts.extend(["-I", "dummy", "--no-video"])

    if not enable_audio_playback:
        cmd_parts.append("--no-audio")

    cmd_parts.append("--quiet")

    if additional_player_options:
        cmd_parts.append(additional_player_options)

    cmd_parts.append('"')

    return cmd_parts


def _build_gpac_command(
    client_config,
    u_id,
    is_headless,
    player_config,
):
    """
    Build the GPAC command based on the client configuration and environment.

    Parameters
    ----------
    client_config : dict
        Configuration for the client, including namespace, destination IP, and port.
    u_id : int
        UID of the invoking user, used for PulseAudio configuration.
    is_headless : bool
        Whether the environment is headless (no GUI).
    player_config : dict
        Configuration for the player,
        including options for audio/video playback and additional GPAC options.
    Returns
    -------
    list
        A list of command parts that can be joined to form the final GPAC command.
    """
    ns_name = client_config["ns_name"]
    destination_ip = client_config["destination_ip"]
    port = client_config["port"]
    enable_audio_playback = bool(player_config.get("enable_audio_playback", True))
    enable_video_playback = bool(player_config.get("enable_video_playback", True))
    additional_player_options = player_config.get("additional_player_options", "")
    cmd_parts = [
        f"ip netns exec {ns_name}",
        "env",
        f"PULSE_SERVER=/run/user/{u_id}/pulse/native",
        f"PULSE_COOKIE=/run/user/{u_id}/pulse/cookie",
    ]

    if is_headless or not enable_video_playback:
        if is_headless:
            print("Headless environment detected — using dummy SDL drivers")
        if not enable_video_playback:
            print("Video playback disabled — using dummy SDL video driver")
        cmd_parts.extend(["SDL_VIDEODRIVER=dummy", "SDL_AUDIODRIVER=dummy"])

    cmd_parts.append('bash -c "')

    cmd_parts.extend(
        [
            "rm -rf /tmp/gpac_cache;",
            "gpac -logs=all@info:ncl",
            "-i",
            (
                f"http://{destination_ip}:{port}/manifest.mpd:"
                "gpac:algo=grate:"
                "start_with=min_bw:"
                "debug_as=0,1"
            ),
        ]
    )

    if enable_video_playback:
        if is_headless:
            cmd_parts.append("compositor:drv=no")
        else:
            cmd_parts.append("vout:buffer=1000:mbuffer=5000:cache=none")
    else:
        cmd_parts.append("compositor:drv=no")

    if enable_audio_playback:
        cmd_parts.append("aout")

    cmd_parts.extend(["-clean-cache", "-sloop"])

    if additional_player_options:
        cmd_parts.append(additional_player_options)

    cmd_parts.append('"')

    return cmd_parts


def run_mpeg_dash_client(
    client_config,
    out,
    err,
    player_config,
):
    """Run MPEG DASH client."""

    u_id, vlc_binary_prefix = _get_user_uid_and_vlc_prefix()
    is_headless = _is_headless_environment()
    player = player_config.get("player")
    if not player:
        raise ValueError("Missing or empty 'player' in player_config")

    logger = logging.getLogger(__name__)
    logger.info("Using player: %s", player)

    if player == "vlc":
        cmd_parts = _build_vlc_command(
            client_config=client_config,
            u_id=u_id,
            vlc_binary_prefix=vlc_binary_prefix,
            is_headless=is_headless,
            player_config=player_config,
        )
    elif player == "gpac":
        cmd_parts = _build_gpac_command(
            client_config=client_config,
            u_id=u_id,
            is_headless=is_headless,
            player_config=player_config,
        )
    else:
        raise ValueError(f"Unsupported player: {player}")

    cmd_string = " ".join(filter(None, cmd_parts))
    duration = client_config.get("duration", None)

    return exec_exp_commands(
        cmd_string,
        stdout=out,
        stderr=err,
        timeout=duration,
    )
