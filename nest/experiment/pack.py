# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Package all results into a folder
import os
import time

from ..user import User

class Pack():

    FOLDER = ''

    @staticmethod
    def init(exp_name):
        """
        Create a folder with format 'testname(time)_dump'

        :param exp_name: Name of experiment
        :type exp_name: string
        """

        timestamp = time.strftime('%d-%m-%Y-%H:%M:%S')
        Pack.FOLDER = '{exp_name}({timestamp})_dump'.format(exp_name = exp_name, timestamp = timestamp)  
        os.mkdir(Pack.FOLDER)
        Pack.set_owner(Pack.FOLDER)
    
    @staticmethod
    def dump_file(filename, content):
        """
        Dump a file into Pack.FOLDER

        :param filename: Name of file
        :type filename: string
        :param content: Content to be stored in file
        :type content: string
        """

        path = os.path.join(Pack.FOLDER, filename)
        with open(path, 'w') as f:
            f.write(content)
        Pack.set_owner(path)

    @staticmethod
    def dump_plot(filename, fig):
        """
        Dump a plot into Pack.FOLDER

        :param filename: Name of plot
        :type filename: string
        :param fig: Plot figure to be stored in file
        :type fig: matplotlib.pyplot.fig
        """

        path = os.path.join(Pack.FOLDER, filename)
        fig.savefig(path)
        Pack.set_owner(path)
            
    @staticmethod
    def set_owner(path):
        """
        Change file permission to that of the
        actual user running (For eg. user running
        sudo)

        :param path: Path of file
        :type path: string
        """

        user_id = User.get_user_id()
        group_id = User.get_group_id()
        os.chown(path, user_id, group_id)

    @staticmethod
    def compress():
        """
        Compress Pack.FOLDER into a tar archive
        """

        pass
