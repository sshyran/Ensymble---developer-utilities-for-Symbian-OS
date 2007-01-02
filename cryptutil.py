#!/usr/bin/env python
# -*- coding: iso8859-1 -*-

##############################################################################
# cryptutil.py - OpenSSL command line utility wrappers for Ensymble
# Copyright 2006, 2007 Jussi Ylänen
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

    if passphrase == None or len(passphrase) == 0:
        # OpenSSL does not like empty stdin while reading a passphrase from it.
        passphrase = "\n"

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

        # Add enclosing quotes to any filename containing whitespace. Quotes
        # are only relevant when creating command lines to execute.
        keyfilename_cmd = keyfilename
        if " " in keyfilename:
            keyfilename_cmd = '"%s"' % keyfilename_cmd

        key2filename_cmd = key2filename
        if " " in key2filename:
            key2filename_cmd = '"%s"' % key2filename_cmd

        sigfilename_cmd = sigfilename
        if " " in sigfilename:
            sigfilename_cmd = '"%s"' % sigfilename_cmd

        stringfilename_cmd = stringfilename
        if " " in stringfilename:
            stringfilename_cmd = '"%s"' % stringfilename_cmd

        # Write PEM format private key to file.
        keyfile = file(keyfilename, "wb")
        keyfile.write(privkey)
        keyfile.close()

        # Decrypt the private key. Older versions of OpenSSL do not
        # accept the "-passin" parameter for the "dgst" command.
        runopenssl("%s -in %s -out %s -passin stdin" %
                   (keytype.convcmd, keyfilename_cmd, key2filename_cmd),
                   passphrase)

        if not os.path.isfile(key2filename):
            # OpenSSL did not create output file. Probably a wrong pass phrase.
            raise ValueError("wrong pass phrase")

        # Write binary string to a file. On some systems, stdin is
        # always in text mode and thus unsuitable for binary data.
        stringfile = file(stringfilename, "wb")
        stringfile.write(string)
        stringfile.close()

        # Sign binary string using the decrypted private key.
        command = ("dgst %s -binary -sign %s "
                   "-out %s %s") % (keytype.signcmd, key2filename_cmd,
                                    sigfilename_cmd, stringfilename_cmd)
        runopenssl(command)

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
    '''Convert X.509 certificates from PEM (base-64) format to DER (binary).

    certtobinary(...) -> dercert

    pemcert     One or more X.509 certificates in PEM (base-64) format, a string

    dercert     X.509 certificate(s), an ASN.1 encoded binary string'''

    # Find base-64 encoded data between header and footer.
    header = "-----BEGIN CERTIFICATE-----"
    footer = "-----END CERTIFICATE-----"
    endoffset = 0
    certs = []
    while True:
        # First find a header.
        startoffset = pemcert.find(header, endoffset)
        if startoffset < 0:
            # No header found, stop search.
            break

        startoffset += len(header)

        # Next find a footer.
        endoffset = pemcert.find(footer, startoffset)
        if endoffset < 0:
            # No footer found.
            raise ValueError("missing PEM certificate footer")

        # Extract the base-64 encoded certificate and decode it.
        try:
            cert = pemcert[startoffset:endoffset].decode("base-64")
        except:
            # Base-64 decoding error.
            raise ValueError("invalid PEM format certificate")

        certs.append(cert)

        endoffset += len(footer)

    if len(certs) == 0:
        raise ValueError("not a PEM format certificate")

    # DER certificates are simply raw binary versions
    # of the base-64 encoded PEM certificates.
    return "".join(certs)


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

def runopenssl(command, datain = ""):
    '''Run the OpenSSL command line tool with the given parameters and data.'''

    global opensslcommand

    if opensslcommand == None:
        # Find path to the OpenSSL command.
        findopenssl()

    # Construct a command line for os.popen3().
    cmdline = '%s %s' % (opensslcommand, command)

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
    '''Find the OpenSSL command line tool.'''

    global opensslcommand

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

    if " " in cmd:
        # Add quotes around command in case of embedded whitespace on path.
        cmd = '"%s"' % cmd

    opensslcommand = cmd


##############################################################################
# Utility classes for module internal use
##############################################################################

class Bunch:
    '''Bunch recipe from Python Cookbook, by Alex Martelli'''
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
