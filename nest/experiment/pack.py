# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Package all results into a folder"""

import os
import time
import shutil

from nest.user import User


class Pack:
    """Handles packaging results"""

    FOLDER = ""

    @staticmethod
    def init(exp_name):
        """
        Create a folder with format 'testname(time)_dump'

        Parameters
        ----------
        exp_name : str
            Name of experiment
        """
        timestamp = time.strftime("%d-%m-%Y-%H:%M:%S")
        Pack.FOLDER = f"{exp_name}({timestamp})_dump"
        os.mkdir(Pack.FOLDER)
        Pack.set_owner(Pack.FOLDER)

    @staticmethod
    def dump_file(filename, content):
        """
        Dump a file into Pack.FOLDER

        Parameters
        ----------
        filename : str
            Name of file
        content : str
            Content to be stored in file
        """
        path = os.path.join(Pack.FOLDER, filename)
        with open(path, "w") as file:
            file.write(content)
        Pack.set_owner(path)

    @staticmethod
    def dump_plot(subfolder, filename, fig):
        """
        Dump a plot into Pack.FOLDER

        Parameters
        ----------
        subfolder : str
            Subfolder to which plot belongs to
        filename : str
            Name of plot
        fig : matplotlib.pyplot.fig
            Plot figure to be stored in file
        """
        Pack.create_subfolder(subfolder)
        path = os.path.join(Pack.FOLDER, subfolder, filename)
        fig.savefig(path)
        Pack.set_owner(path)

    @staticmethod
    def create_subfolder(subfolder):
        """
        Create subfolder if it already doesn't exist

        Parameters
        ----------
        subfolder : str
            Subfolder name
        """
        path = os.path.join(Pack.FOLDER, subfolder)
        if not os.path.isdir(path):
            os.mkdir(path)
            Pack.set_owner(path)

    @staticmethod
    def set_owner(path):
        """
        Change file permission to that of the
        actual user running (For example, user running
        sudo)

        Parameters
        ----------
        path : str
            Path of file
        """

        user_id = User.user_id
        group_id = User.group_id
        os.chown(path, user_id, group_id)

    @staticmethod
    def compress():
        """Compress Pack.FOLDER into a tar archive"""
        # TODO

    @staticmethod
    def copy_files(src_path, dst_path=None):
        """
        Copies file from source to stats folder

        Parameters
        ----------
        src_path : str
            Path of source file
        dst_path : str
            Relative Path of destination inside the stats folder
        """

        if dst_path is None:
            # Default destination path is stats folder
            dst_path = Pack.FOLDER
        else:
            dst_path = os.path.join(Pack.FOLDER, dst_path)

        shutil.copy(src_path, dst_path)
        filename = os.path.join(dst_path, os.path.basename(src_path))
        Pack.set_owner(filename)

    @staticmethod
    def move_files(src_path, dst_path=None):
        """
        Copies file from source to stats folder

        Parameters
        ----------
        src_path : str
            Path of source file
        dst_path : str
            Relative Path of destination inside the stats folder
        """

        if dst_path is None:
            # Default destination path is stats folder
            dst_path = Pack.FOLDER
        else:
            dst_path = os.path.join(Pack.FOLDER, dst_path)

        shutil.move(src_path, dst_path)
        filename = os.path.join(dst_path, os.path.basename(src_path))
        Pack.set_owner(filename)
