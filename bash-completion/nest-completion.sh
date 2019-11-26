# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019 NITK Surathkal

#!/bin/bash

_nest_completion()
{
    if [ "${#COMP_WORDS[@]}" != "2" ]; then
        return
    fi
    if [[ "${COMP_WORDS[1]}" == -* ]]; then
        COMPREPLY=( $(compgen -W '--help -h --version' -- "${COMP_WORDS[1]}" ) )
    fi
    
}

complete -F _nest_completion nest