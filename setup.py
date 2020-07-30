# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get version
version = {}
with open("nest/version.py") as fp:
    exec(fp.read(), version)

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='nitk-nest',
    version=version['__version__'],
    description='NeST: Network Stack Tester',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://nitk-nest.github.io/',
    author='NITK',
    author_email='nest.nitk@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='network, namespace, linux',
    packages=find_packages(),
    package_data={
        "nest.experiment.parser": ["iterators/*.sh"],
        "nest": ["config.json"]
    },
    python_requires='>=3.6, <4',
    install_requires=[
        'matplotlib',
        'numpy',
        'packaging'
    ],
    project_urls={
        'Source': 'https://gitlab.com/nitk-nest/nest',
    },
)