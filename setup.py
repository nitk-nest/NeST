# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import pathlib
import sys
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()

# Get version
version = {}
with open("nest/version.py") as fp:
    exec(fp.read(), version)

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Check for pip versions below 9.0.0
if sys.version_info < (3, 6) or sys.version_info >= (4, 0):
    raise RuntimeError("This package requires Python version >=3.6 and <4")

setup(
    name="nest",
    version=version["__version__"],
    description="NeST: Network Stack Tester",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://nest.nitk.ac.in/",
    author="NITK",
    author_email="nest@nitk.edu.in",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="network, namespace, linux",
    packages=find_packages(),
    package_data={
        "nest.experiment": ["info/README.txt"],
        "nest.experiment.parser": ["iterators/*.sh"],
        "nest": ["config.json"],
    },
    python_requires=">=3.6, <4",
    install_requires=["matplotlib", "numpy", "packaging", "tqdm"],
    project_urls={
        "Source": "https://gitlab.com/nitk-nest/nest",
    },
)
