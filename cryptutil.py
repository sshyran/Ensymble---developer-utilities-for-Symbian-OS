#!/usr/bin/env python
# -*- coding: iso8859-1 -*-

##############################################################################
# cryptutil.py - OpenSSL command line utility wrappers for Ensymble
# Copyright 2006 Jussi Ylänen
#
# This file is part of Ensymble developer utilities for Symbian OS(TM).
#
# Ensymble is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ensymble is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ensymble; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
##############################################################################

import os
import errno
import tempfile
import random


opensslcommand = None   # Path to OpenSSL command line tool
openssldebug   = False  # True for extra debug output


##############################################################################
# Public module-level functions
##############################################################################

def setdebug(active):
    '''Activate or deactivate debug output.

    setdebug(...) -> None

    active      Debug output enabled / disabled, a boolean value

    Debug output consists of OpenSSL binary command line and
    any output produced to the standard error stream by OpenSSL.
    '''

    global openssldebug
    openssldebug =  not not active  # Convert to boolean.

def signstring(privkey, passphrase, string):
    '''Sign a binary string using a given private key and its pass phrase.

    signstring(...) -> (signature, keytype)

    privkey     RSA or DSA private key, a string in PEM (base-64) format
    passphrase  pass phrase for the private key, a non-Unicode string or None
    string      a binary string to sign

    signature   signature, an ASN.1 encoded binary string
    keytype     detected key type, string, "RSA" or "DSA"

    NOTE: On platforms with poor file system security, unencrypted version
    of the private key may be grabbed from the temporary directory!'''

    if passphrase == None:
        passphrase = ""

    # Create a temporary directory for OpenSSL to work in.
    tempdir = mkdtemp("ensymble-XXXXXX")

    # Determine key type.
    if privkey.find("-----BEGIN DSA PRIVATE KEY-----") >= 0:
        keytype = Bunch(name = "DSA", convcmd = "dsa", signcmd = "-dss1")
    elif privkey.find("-----BEGIN RSA PRIVATE KEY-----") >= 0:
        keytype = Bunch(name = "RSA", convcmd = "rsa", signcmd = "-sha1")
    else:
        raise ValueError("not an RSA or DSA private key in PEM format")

    try:
        keyfilename     = os.path.join(tempdir, "privkey.pem")
        key2filename    = os.path.join(tempdir, "privkey2.pem")
        sigfilename     = os.path.join(tempdir, "signature.dat")
        stringfilename  = os.path.join(tempdir, "string.dat")

        # Write PEM format private key to file.
        keyfile = file(keyfilename, "wb")
        keyfile.write(privkey)
        keyfile.close()

        # Decrypt the private key. Older versions of OpenSSL do not
        # accept the "-passin" parameter for the "dgst" command.
        runopenssl(tempdir, "%s -in privkey.pem -out privkey2.pem "
                   "-passin stdin" % keytype.convcmd, passphrase + "\n")

        if not os.path.isfile(key2filename):
            # OpenSSL did not create output file. Probably a wrong pass phrase.
            raise ValueError("wrong pass phrase")

        # Write binary string to a file. On some systems, stdin is
        # always in text mode and thus unsuitable for binary data.
        stringfile = file(stringfilename, "wb")
        stringfile.write(string)
        stringfile.close()

        # Sign binary string using the decrypted private key.
        command = ("dgst %s -binary -sign privkey2.pem "
                   "-out signature.dat string.dat") % keytype.signcmd
        runopenssl(tempdir, command)

        # Check that the signature was successfully generated.
        if not os.path.isfile(sigfilename):
            raise ValueError("unspecified error during signing")

        # Read signature from file.
        sigfile = file(sigfilename, "rb")
        signature = sigfile.read()
        sigfile.close()
    finally:
        # Delete temporary files.
        for fname in (keyfilename, key2filename, sigfilename, stringfilename):
            try:
                os.remove(fname)
            except OSError:
               pass

        # Remove temporary directory.
        os.rmdir(tempdir)

    return (signature, keytype.name)


def certtobinary(pemcert):
    '''Convert an X.509 certificate from PEM (base-64) format to DER (binary).

    certtobinary(...) -> dercert

    pemcert     X.509 certificate in PEM (base-64) format

    dercert     X.509 certificate in DER (binary) format'''

    resp = runopenssl(None, "x509 -inform pem -outform der", pemcert)

    if resp[1] != "" or resp[0] == "":
        # Conversion did not succeed.
        raise ValueError("certificate conversion error (invalid certificate?)")

    return resp[0]


##############################################################################
# Module-level functions which are normally only used by this module
##############################################################################

def mkdtemp(template):
    '''
    Create a unique temporary directory.

    tempfile.mkdtemp() was introduced in Python v2.3. This is for
    backward compatibility.
    '''

    # Cross-platform way to determine a suitable location for temporary files.
    systemp = tempfile.gettempdir()

    if not template.endswith("XXXXXX"):
        raise ValueError("invalid template for mkdtemp(): %s" % template)

    for n in xrange(10000):
        randchars = []
        for m in xrange(6):
            randchars.append(random.choice("abcdefghijklmnopqrstuvwxyz"))

        tempdir = os.path.join(systemp, template[: -6]) + "".join(randchars)

        try:
            os.mkdir(tempdir, 0700)
            return tempdir
        except OSError:
            pass
    else:
        # All unique names in use, raise an error.
        raise OSError(errno.EEXIST, os.strerror(errno.EEXIST),
                      os.path.join(systemp, template))

def runopenssl(tempdir, command, datain = ""):
    '''Run an OpenSSL command in a previously created temporary directory.'''

    # Find path to the OpenSSL command.
    findopenssl()

    # Construct a command line for os.popen3().
    if tempdir != None:
        # Run OpenSSL command in a temporary directory.
        # The "&&" command separator works with Bourne Shell
        # (Unix-like systems) and cmd.exe (Windows).
        cmdline = 'cd "%s" && "%s" %s' % (tempdir, opensslcommand, command)
    else:
        # No files to use or generate, no temporary directory needed.
        cmdline = '"%s" %s' % (opensslcommand, command)

    if openssldebug:
        # Print command line.
        print "DEBUG: os.popen3(%s)" % repr(cmdline)

    # Run command. Use os.popen3() to capture stdout and stderr.
    pipein, pipeout, pipeerr = os.popen3(cmdline)
    pipein.write(datain)
    pipein.close()
    dataout = pipeout.read()
    pipeout.close()
    errout = pipeerr.read()
    pipeerr.close()

    if openssldebug:
        # Print standard error output.
        print "DEBUG: pipeerr.read() = %s" % repr(errout)

    return (dataout, errout)

def findopenssl():
    '''Find OpenSSL command line tool.'''

    global opensslcommand

    if opensslcommand != None:
        # OpenSSL already found, do nothing.
        return

    # Get PATH and split it to a list of paths.
    paths = os.environ["PATH"].split(os.pathsep)

    for path in paths:
        cmd = os.path.join(path, "openssl")
        try:
            # Try to query OpenSSL version.
            pin, pout = os.popen4('"%s" version' % cmd)
            pin.close()
            verstr = pout.read()
            pout.close()
        except OSError:
            # Could not run command, skip to the next path candidate.
            continue

        if verstr.split()[0] == "OpenSSL":
            # Command found, stop searching.
            break
    else:
        raise IOError("no valid OpenSSL command line tool found in PATH")

    opensslcommand = cmd


##############################################################################
# Utility classes for module internal use
##############################################################################

class Bunch:
    '''Bunch recipe from Python Cookbook, by Alex Martelli'''
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
