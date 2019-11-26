# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019 NITK Surathkal

#!/bin/bash

curr_path="$(pwd)"

#To start from a new line
echo "" >> ~/.bashrc

#Letting nest.py to be executed from any folder
echo "export PATH=\$PATH:${curr_path}/" >> ~/.bashrc

#Letting nest.py executed also using nest command
echo "alias nest='run-nest.py'" >> ~/.bashrc

#Add nest manpage to system
mkdir -p /usr/local/man/man1
cp man/nest.1 /usr/local/man/man1/nest.1
gzip /usr/local/man/man1/nest.1

#Add bash-completion
cp bash-completion/nest-completion.sh /usr/share/bash-completion/completions/
echo "source /usr/share/bash-completion/completions/nest-completion.sh" >> ~/.bashrc

#Equivalent to compiling the ~/.bashrc file
source ~/.bashrc