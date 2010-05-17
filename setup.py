#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

name    = "ensymble"
version = "0.29"
url     = "http://code.google.com/p/ensymble/"
download_url = "%s/detail?name=%s-%s.tar.gz" % (url, name, version)

"http://code.google.com/p/ensymble/downloads/detail?name=ensymble-0.28.tar.gz"
long_description = """
The Ensymble developer utilities for Symbian OS™ is a collection of Python®
modules and command line programs for Symbian OS software development.

Current focus of Ensymble development is to provide useful tools for making
Python for S60 (PyS60) programs. A long term goal of Ensymble is to provide a
cross-platform, open-source way to do Symbian OS software development,
supporting Symbian OS versions 9.1 and later.

SIS files made with Ensymble work from S60 3rd Edition phones onwards. For 1st
and 2nd Edition phones there's py2sisng.
"""

setup( name = name,
       version = version,
       description = "Tools to make PyS60 applications for Symbian S60 phones",
       author = "Jussi Ylänen",
       maintainer = "Steven Fernandez",
       maintainer_email = "steve@lonetwin.net",
       url = url,
       long_description = long_description,
       download_url = download_url,
       packages = ['ensymble', 'ensymble.actions', 'ensymble.utils'],
       scripts  = ['ensymble.py']
    )
