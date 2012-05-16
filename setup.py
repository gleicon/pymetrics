import sys, os, os.path, subprocess
from setuptools.command import easy_install
import pkg_resources as pkgrsrc

from setuptools import setup
from distutils import log
log.set_threshold(log.INFO)

setup(
        name            = "pymetrics",
        version         = "0.1",

        packages        =   ['pymetrics'],
        install_requires = ['redis>=2.4.10'],

        # metadata for upload to PyPI
        author          = "Gleicon Moraes",
        author_email    = "gleicon@gmail.com",
        keywords        = "metrics redis",
        description     = "simple python metrics",
        url             = "https://github.com/gleicon/pymetrics",
    )

