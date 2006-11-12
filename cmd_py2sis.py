#!/usr/bin/env python
# -*- coding: iso8859-1 -*-

##############################################################################
# cmd_py2sis.py - Ensymble command line tool, py2sis command
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

import sys
import os
import re
import getopt
import getpass
import locale
import zlib

import sisfile
import sisfield
import symbianutil
import rscfile
import miffile


##############################################################################
# Help texts
##############################################################################

shorthelp = 'Emulate "Python for S60" packaging tool "py2sis"'
longhelp  = '''py2sis
    [--uid=0x01234567] [--appname=AppName] [--version=1.0.0]
    [--lang=EN,...] [--icon=icon.svg]
    [--shortcaption="App. Name",...] [--caption="Application Name",...]
    [--cert=mycert.pem] [--privkey=mykey.pem] [--passphrase=12345]
    [--caps=Cap1+Cap2+...] [--encoding=terminal,filesystem] [--verbose]
    <src> [sisfile]

Emulate "Python for S60" packaging tool "py2sis", i.e. create a
SIS package from "Python for S60" script and auxiliary files.

Options:
    src          - Source script or directory
    sisfile      - Path of the created SIS file
    uid          - Symbian UID for the application
    appname      - Name of the application
    version      - Application version: X.Y.Z or X,Y,Z (major, minor, build)
    lang         - Comma separated list of two-character language codes
    icon         - Icon file in SVG-Tiny format
    shortcaption - Comma separated list of short captions in all languages
    caption      - Comma separated list of long captions in all languages
    cert         - Certificate to use for signing (PEM format)
    privkey      - Private key of the certificate (PEM format)
    passphrase   - Pass phrase of the private key (insecure, use stdin instead)
    caps         - Capability names, separated by "+" (none by default)
    encoding     - Local character encodings for terminal and filesystem
    verbose      - Print extra statistics

If no certificate and its private key are given, a default self-signed
certificate is used to sign the SIS file. Software authors are encouraged
to create their own unique certificates for SIS packages that are to be
distributed.

If no icon is given, the Python logo is used as the icon. The Python
logo is a trademark of the Python Software Foundation.
'''


##############################################################################
# Parameters
##############################################################################

MAXPASSPHRASELENGTH     = 256
MAXCERTIFICATELENGTH    = 65536
MAXPRIVATEKEYLENGTH     = 65536
MAXICONFILESIZE         = 65536


##############################################################################
# Public module-level functions
##############################################################################

def run(pgmname, argv):
    # Determine system character encodings.
    try:
        # getdefaultlocale() may sometimes return None.
        # Fall back to ASCII encoding in that case.
        terminalenc = locale.getdefaultlocale()[1] + ""
    except TypeError:
        # Invalid locale, fall back to ASCII terminal encoding.
        terminalenc = "ascii"

    try:
        # sys.getfilesystemencoding() was introduced in Python v2.3 and
        # it can sometimes return None. Fall back to ASCII if something
        # goes wrong.
        filesystemenc = sys.getfilesystemencoding() + ""
    except (AttributeError, TypeError):
        filesystemenc = "ascii"

    try:
        gopt = getopt.gnu_getopt
    except:
        # Python <v2.3, GNU-style parameter ordering not supported.
        gopt = getopt.getopt

    # Parse command line arguments.
    short_opts = "u:n:r:l:i:s:c:a:k:p:b:e:vh"
    long_opts = [
        "uid=", "appname=", "version=", "lang=", "icon=",
        "shortcaption=", "caption=", "cert=", "privkey=", "passphrase=",
        "caps=", "encoding=", "verbose", "debug", "help"
    ]
    args = gopt(argv, short_opts, long_opts)

    opts = dict(args[0])
    pargs = args[1]

    if len(pargs) == 0:
        raise ValueError("no source file name given")

    # Override character encoding of command line and filesystem.
    encs = opts.get("--encoding", opts.get("-e", "%s,%s" % (terminalenc,
                                                            filesystemenc)))
    try:
        terminalenc, filesystemenc = encs.split(",")
    except (ValueError, TypeError):
        raise ValueError("invalid encoding string '%s'" % encs)

    # Get source name, either a Python program or a directory.
    src = pargs[0].decode(terminalenc).encode(filesystemenc)
    if os.path.isdir(src):
        # Remove trailing slashes (or whatever the separator is).
        src = os.path.split(src + os.sep)[0]

        # Use last directory component as the name.
        basename = os.path.basename(src)

        # Source is a directory, recursively collect files it contains.
        srcdir = src
        srcfiles = []
        prefixlen = len(srcdir) + len(os.sep)
        def getfiles(arg, dirname, names):
            for name in names:
                path = os.path.join(dirname, name)
                if not os.path.isdir(path):
                    arg.append(path[prefixlen:])
        os.path.walk(srcdir, getfiles, srcfiles)

        # Read application version and UID3 from default.py.
        version, uid3 = scandefaults(os.path.join(srcdir, "default.py"))
    else:
        if src.lower().endswith(".py"):
            # Use program name without the .py extension.
            basename = os.path.basename(src)[:-3]
        else:
            # Unknown extension, use program name as-is.
            basename = os.path.basename(src)

        # Source is a file, use it.
        srcdir, srcfiles = os.path.split(src)
        srcfiles = [srcfiles]

        # Read application version and UID3 from file.
        version, uid3 = scandefaults(os.path.join(srcdir, srcfiles[0]))

    # Parse version string, use 1.0.0 by default.
    version = opts.get("--version", opts.get("-r", version))
    if version == None:
        version = "1.0.0"
        print ("%s: warning: no application version given, "
               "using %s" % (pgmname, version))
    try:
        version = parseversion(version)
    except (ValueError, IndexError, TypeError):
        raise ValueError("invalid version string '%s'" % version)

    # Determine output SIS file name.
    if len(pargs) == 1:
        # Derive output file name from input file name.
        outfile = "%s_v%d_%d_%d.sis" % (basename, version[0],
                                        version[1], version[2])
    elif len(pargs) == 2:
        outfile = pargs[1].decode(terminalenc).encode(filesystemenc)
        if os.path.isdir(outfile):
            # Output to directory, derive output name from input file name.
            outfile = os.path.join(sisfile, "%s_v%d_%d_%d.sis" % (
                basename, version[0], version[1], version[2]))
        if not outfile.lower().endswith(".sis"):
            outfile += ".sis"
    else:
        raise ValueError("wrong number of arguments")

    # Determine application name (install dir.), use basename by default.
    appname = opts.get("--appname", opts.get("-n", basename))
    appname = appname.decode(terminalenc)

    # Get UID3.
    uid3 = opts.get("--uid", opts.get("-u", uid3))
    if uid3 == None:
        # No UID given, auto-generate a test UID from application name.
        uid3 = (symbianutil.crc32ccitt(appname.lower()) &
                0x0fffffffL) | 0xe0000000L
        print ("%s: warning: no UID given, using auto-generated "
               "test UID 0x%08x" % (pgmname, uid3))
    elif uid3.lower().startswith("0x"):
        # Prefer hex UIDs with leading "0x".
        uid3 = long(uid3, 16)
    else:
        try:
            if len(uid3) == 8:
                # Assuming hex UID even without leading "0x".
                print ('%s: warning: assuming hex UID even '
                       'without leading "0x"' % pgmname)
                uid3 = long(uid3, 16)
            else:
                # Decimal UID.
                uid3 = long(uid3)
                print ('%s: warning: decimal UID converted to 0x%08x' %
                       (pgmname, uid3))
        except ValueError:
            raise ValueError("invalid UID string '%s'" % uid3)

    # Determine application language(s), use "EN" by default.
    lang = opts.get("--lang", opts.get("-l", "EN")).split(",")
    numlang = len(lang)

    # Get icon file name.
    icon = opts.get("--icon", opts.get("-i", None))
    if icon != None:
        icon = icon.decode(terminalenc).encode(filesystemenc)

        # Read icon file.
        f = file(icon, "rb")
        icondata = f.read(MAXICONFILESIZE + 1)
        f.close()

        if len(icondata) > MAXICONFILESIZE:
            raise ValueError("icon file too large")
    else:
        # No icon given, use a default icon.
        icondata = zlib.decompress(defaulticondata.decode("base-64"))

    # Determine application short caption(s).
    shortcaption = opts.get("--shortcaption", opts.get("-s", ""))
    shortcaption = shortcaption.decode(terminalenc)
    if len(shortcaption) == 0:
        # Short caption not given, use application name.
        shortcaption = [appname] * numlang
    else:
        shortcaption = shortcaption.split(",")

    # Determine application long caption(s), use short caption by default.
    caption = opts.get("--caption", opts.get("-c", ""))
    caption = caption.decode(terminalenc)
    if len(caption) == 0:
        # Caption not given, use short caption.
        caption = shortcaption
    else:
        caption = caption.split(",")

    # Compare the number of languages and captions.
    if len(shortcaption) != numlang or len(caption) != numlang:
        raise ValueError("invalid number of captions")

    # Get certificate file name.
    cert = opts.get("--cert", opts.get("-a", None))
    if cert != None:
        cert = cert.decode(terminalenc).encode(filesystemenc)

        # Read certificate file.
        f = file(cert, "rb")
        certdata = f.read(MAXCERTIFICATELENGTH + 1)
        f.close()

        if len(certdata) > MAXCERTIFICATELENGTH:
            raise ValueError("certificate file too large")
    else:
        # No certificate given, use a default certificate.
        certdata = zlib.decompress(defaultcertdata.decode("base-64"))

    # Get private key file name.
    privkey = opts.get("--privkey", opts.get("-k", None))
    if privkey != None:
        privkey = privkey.decode(terminalenc).encode(filesystemenc)

        # Read private key file.
        f = file(privkey, "rb")
        privkeydata = f.read(MAXPRIVATEKEYLENGTH + 1)
        f.close()

        if len(privkeydata) > MAXPRIVATEKEYLENGTH:
            raise ValueError("private key file too large")
    else:
        # No private key given, use a default private key.
        privkeydata = zlib.decompress(defaultprivkeydata.decode("base-64"))

    if (cert != None and privkey == None) or (cert == None and privkey != None):
        raise ValueError("missing certificate or private key")
    elif cert == None and privkey == None:
        print ("%s: warning: no certificate given, using "
               "insecure built-in one" % pgmname)

        # Warn if the UID is in the protected range.
        # Resulting SIS file will probably not install.
        if uid3 < 0x80000000L:
            print ("%s: warning: UID is in the protected range "
                   "(0x00000000 - 0x7ffffff)" % pgmname)

    # Get pass phrase. Pass phrase remains in terminal encoding.
    passphrase = opts.get("--passphrase", opts.get("-p", None))
    if passphrase == None and privkey != None:
        # Private key given without "--passphrase" option, ask it.
        if sys.stdin.isatty():
            # Standard input is a TTY, ask password interactively.
            passphrase = getpass.getpass("Enter private key pass phrase:")
        else:
            # Not connected to a TTY, read stdin non-interactively instead.
            passphrase = sys.stdin.read(MAXPASSPHRASELENGTH + 1)

            if len(passphrase) > MAXPASSPHRASELENGTH:
                raise ValueError("pass phrase too long")

            passphrase = passphrase.strip()

    # Get capabilities and normalize the names.
    caps = opts.get("--caps", opts.get("-b", ""))
    capmask = symbianutil.capstringtomask(caps)
    caps = symbianutil.capmasktostring(capmask, True)

    # Determine verbosity.
    verbose = False
    if "--verbose" in opts.keys() or "-v" in opts.keys():
        verbose = True

    # Determine if debug output is requested.
    debug = False
    if "--debug" in opts.keys():
        debug = True

        # Enable debug output for OpenSSL-related functions.
        import cryptutil
        cryptutil.setdebug(True)

    # Ingredients for successful SIS generation:
    #
    # terminalenc   Terminal character encoding (autodetected)
    # filesystemenc File system name encoding (autodetected)
    # basename      Base for generated file names on host, filesystemenc encoded
    # srcdir        Directory of source files, filesystemenc encoded
    # srcfiles      List of filesystemenc encoded source file names in srcdir
    # outfile       Output SIS file name, filesystemenc encoded
    # uid3          application UID3, long integer
    # appname       Application name and install directory in device, in Unicode
    # version       A triple-item tuple (major, minor, build)
    # lang          List of two-character language codes, ASCII strings
    # icon          Icon data, a binary string typically containing a SVG-T file
    # shortcaption  List of Unicode short captions, one per language
    # caption       List of Unicode long captions, one per language
    # cert          Certificate in PEM format
    # privkey       Certificate private key in PEM format
    # passphrase    Pass phrase of private key, terminalenc encoded string
    # caps, capmask Capability names and bitmask
    # verbose       Boolean indicating verbose terminal output

    if verbose:
        print
        print "Input file(s)     %s"        % " ".join(
            [s.decode(filesystemenc).encode(terminalenc) for s in srcfiles])
        print "Output SIS-file   %s"        % (
             outfile.decode(filesystemenc).encode(terminalenc))
        print "UID               0x%08x"    % uid3
        print "Application name  %s"        % appname.encode(terminalenc)
        print "Version           %d.%d.%d"  % (
            version[0], version[1], version[2])
        print "Language(s)       %s"        % ", ".join(lang)
        print "Icon              %s"        % ((icon and
            icon.decode(filesystemenc).encode(terminalenc)) or "<default>")
        print "Short caption(s)  %s"    % ", ".join(
            [s.encode(terminalenc) for s in shortcaption])
        print "Long caption(s)   %s"    % ", ".join(
            [s.encode(terminalenc) for s in caption])
        print "Certificate       %s"        % ((cert and
            cert.decode(filesystemenc).encode(terminalenc)) or "<default>")
        print "Private key       %s"        % ((privkey and
            privkey.decode(filesystemenc).encode(terminalenc)) or "<default>")
        print "Capabilities      0x%x (%s)" % (capmask, caps)
        print

    # Generate SimpleSISWriter object.
    sw = sisfile.SimpleSISWriter(lang, caption, uid3, version, "Ensymble",
                                 ["Ensymble"] * numlang)

    # Generate an EXE stub and add it to the SIS object.
    exetarget = u"!:\\sys\\bin\\%s_0x%08x.exe" % (appname, uid3)
    string = execstubdata.decode("base-64")
    string = symbianutil.e32imagecrc(string, uid3, uid3, None, capmask)
    sw.addfile(string, exetarget, None, capabilities = capmask)
    del string

    # Generate "Python for S60" resource file.
    rsctarget = u"!:\\resource\\apps\\%s_0x%08x.rsc" % (appname, uid3)
    string = zlib.decompress(pythons60rscdata.decode("base-64"))
    sw.addfile(string, rsctarget)
    del string

    # Generate registration resource file.
    regtarget = u"!:\\private\\10003a3f\\import\\apps\\%s_0x%08x_reg.rsc" % (
        appname, uid3)
    exename = u"%s_0x%08x" % (appname, uid3)
    locpath = u"\\resource\\apps\\%s_0x%08x_loc" % (appname, uid3)
    rw = rscfile.RSCWriter(uid2 = 0x101f8021, uid3 = uid3)
    # STRUCT APP_REGISTRATION_INFO from appinfo.rh
    res = rscfile.Resource(["LONG", "LLINK", "LTEXT", "LONG", "LTEXT", "LONG",
                            "BYTE", "BYTE", "BYTE", "BYTE", "LTEXT", "BYTE",
                            "WORD", "WORD", "WORD", "LLINK"],
                           0, 0, exename, 0, locpath, 1,
                           0, 0, 0, 0, "", 0,
                           0, 0, 0, 0)
    rw.addresource(res)
    string = rw.tostring()
    del rw
    sw.addfile(string, regtarget)
    del string

    # Generate localisable icon/caption definition resource files.
    iconpath = "\\resource\\apps\\%s_0x%08x_aif.mif" % (appname, uid3)
    for n in xrange(numlang):
        loctarget = u"!:\\resource\\apps\\%s_0x%08x_loc.r%02d" % (
            appname, uid3, symbianutil.langidtonum[lang[n]])
        rw = rscfile.RSCWriter(uid2 = 0, offset = "    ")
        # STRUCT LOCALISABLE_APP_INFO from appinfo.rh
        res = rscfile.Resource(["LONG", "LLINK", "LTEXT",
                                "LONG", "LLINK", "LTEXT",
                                "WORD", "LTEXT", "WORD", "LTEXT"],
                               0, 0, shortcaption[n],
                               0, 0, caption[n],
                               1, iconpath, 0, "")
        rw.addresource(res)
        string = rw.tostring()
        del rw
        sw.addfile(string, loctarget)
        del string

    # Generate MIF file for icon.
    icontarget = "!:\\resource\\apps\\%s_0x%08x_aif.mif" % (appname, uid3)
    mw = miffile.MIFWriter()
    mw.addfile(icondata)
    del icondata
    string = mw.tostring()
    del mw
    sw.addfile(string, icontarget)
    del string

    # Add files to SIS object.
    if len(srcfiles) == 1:
        # Read file.
        f = file(os.path.join(srcdir, srcfiles[0]), "rb")
        string = f.read()
        f.close()

        # Add file to the SIS object. One file only, rename it to default.py.
        target = "default.py"
        sw.addfile(string, "!:\\private\\%08x\\%s" % (uid3, target))
        del string
    else:
        # More than one file, use original path names.
        for srcfile in srcfiles:
            # Read file.
            f = file(os.path.join(srcdir, srcfile), "rb")
            string = f.read()
            f.close()

            # Add file to the SIS object.
            target = srcfile.decode(filesystemenc).replace(os.sep, "\\")
            sw.addfile(string, "!:\\private\\%08x\\%s" % (uid3, target))
            del string

    # Add target device dependency.
    sw.addtargetdevice(0x101f7961L, (0, 0, 0), None,
                       ["Series60ProductID"] * numlang)

    # Add "Python for S60" dependency, version 1.3.8 onwards.
    sw.adddependency(0xf0201510L, (1, 3, 8), None,
                     ["Python for S60"] * numlang)

    # Add certificate.
    sw.addcertificate(privkeydata, certdata, passphrase)

    # Generate SIS file out of the SimpleSISWriter object.
    sw.tofile(outfile)


##############################################################################
# Module-level functions which are normally only used by this module
##############################################################################

def scandefaults(filename):
    '''Scan a Python source file for application version string and UID3.'''

    version = None
    uid3    = None

    # Regular expression for the version string. Version may optionally
    # be enclosed in double or single quotes.
    version_ro = re.compile(r'SIS_VERSION\s*=\s*(?:(?:"([^"]*)")|'
                            r"(?:'([^']*)')|(\S+))")

    # Original py2is uses a regular expression
    # r"SYMBIAN_UID\s*=\s*(0x[0-9a-fA-F]{8})".
    # This version is a bit more lenient.
    uid3_ro = re.compile(r"SYMBIAN_UID\s*=\s*(\S+)")

    # First match of each regular expression is used.
    f = file(filename, "rb")
    try:
        while version == None or uid3 == None:
            line = f.readline()
            if line == "":
                break
            if version == None:
                mo = version_ro.search(line)
                if mo:
                    # Get first group that matched in the regular expression.
                    version = filter(None, mo.groups())[0]
            if uid3 == None:
                mo = uid3_ro.search(line)
                if mo:
                    uid3 = mo.group(1)
    finally:
        f.close()
    return version, uid3

def parseversion(version):
    '''Parse a version string: "v1.2.3" or similar.

    Initial "v" can optionally be a capital "V" or omitted altogether. Minor
    and build numbers can also be omitted. Separator can be a comma or a
    period.'''

    version = version.strip().lower()

    # Strip initial "v" or "V".
    if version[0] == "v":
        version = version[1:]

    if "." in version:
        parts = [int(n) for n in version.split(".")]
    else:
        parts = [int(n) for n in version.split(",")]

    # Allow missing minor and build numbers.
    parts.extend([0, 0])

    return parts[0:3]


##############################################################################
# Embedded data: EXE stub, default certificate, private key and icon, resource
##############################################################################

# This is the Symbian application stub, which starts the Python interpreter
# and loads default.py. It is represented here as a base-64-encoded string.
# The stub needs to be patched with correct UID3, Secure ID and capabilities.
# After that, a couple of checksums need to be updated. Function
# e32imagecrc(...) in module symbianutils takes care of all that.
#
# This stub will examine process SID and report that as the UID3 for the
# GUI framework. Therefore, no code parts need to be patched at all.
execstubdata = '''
    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
    ey9synTLgyLZTMIy/ElM4mOC8BOZP3wLw+SmeV7oa+yUmY/uwI9n7xn8KZI+CDTufgg07l/KUzWI
    Jn4BwP5Q6fBg2exP0/pQWi9ksJr1hcvWDrrC22B48cTVItH+sDe5SgwD7AYMO4CZ2EMdukMZVhZX
    AwVhcHWFUdeL+deGXXj7xxVulBg3sq8V314S44Q44bccez8DcAfojix/HHqnjja44a6wR1hbfWCu
    LQvopQW3+wGXslht6wU1haLWHs3A26wvfrCJYGKsF+BvFg+4FBYew9YMtYV5gcJGLCLXiwvXjFeB
    4McK8cP/HGIMa/vI4XLBs9YQfjhrxxBuOKI1glrCH6w7b1hwsC2WF88CtTghfGWGO+VK6LSWv9jD
    DGoYHz+37POD/2g1Gg1XV562t7coPbH/PqJcvY9bxTzPaq7uy1HX/a12tyShzvPannurf1dVr9hq
    NXqOsyaZq+t+1qddr9Xkk6ys9Dn+rg19j12r1+Tc3Q6vnYNXrtTLl63+rVXeSYmwP8L0X97Y5p1e
    yVoK4yun5S65XVZnccrZ10WOrHx4/uR7ZaitrK/u5DMjvZG3keDInSNxI8WR48ifI8qRupHnSIL5
    jBwbjyI9hHXj6yPdx9UtrFrtbsVvBW3C3ireOtjLKV8ivs6/T19zyX//'''

# Default certificate, totally insecure, for testing only!
# Base-64-encoded, zlib-compressed PEM data (which is itself base-64 encoded...)
defaultcertdata = '''
    eJxtksuSokAURPd8xeyNDqAF1GW9Ggqo0oICgZ0vEFAR0UH4+tFezGKm7zIjIzLuyfz4eB0kNuW/
    EAkk/aIISPIWPxRGKbIxQiC1C9BTCArqAq8c3GU9VtS9MKDZKGztkG6nWBAIRQQYZE8iwQoWPFYg
    YBKR+LGbnu7p+Xli0EiwBJ8M1wOXxGAV6flX89LYv1pPRhIoDMxtoEcEPBkN1uZ4WOvl1o76Ipv3
    WKSu12T0+HvHwXc6wEWqAUZtFzQ2BB6fKbp/5r43LPPTxjQfzdbaZwJi/rhd9XEsZ7rFh/CpNRPs
    r7XJdbNi5RXZQuNJN9w0PMkV3Ur9Mstb7QHvy3uzOJTVmH8hXF3CaUV970bbeuHLRItMWZ4RaYO6
    mx93k9bTsjYyVko3CYw8S6HlDL2705l/aERYJZE6DJ65N8r5thIgNU1QMAiAXe0xHBjU3m/vcSHW
    CoRhwTfUmoqz4djHY+HWVuuceFJJFY0Qv0k7ISMrDKziB6/y12yR5Aqjb7I/g10jJFDTlfLKjAFl
    46vNd41OwAiUAAPhqD91DowXbXr7LLoGW8DsuvosO6xHahao8WYeKtVCvfOmc2jF9suWWe0tflza
    0bhdzu0jr/noGury5GSpSeGB8Xho05TlexRNpU3UHisnvaF4pu/IvNNEfU1Gui1Xvdt4QmhqF+3l
    /f6ZlUd0rXHdGmxHb+q2y4Ju9lvGT9OaK1SPD7UeL1auZomdGyjfCycc/7/6P+Pc9Q0='''

# Default certificate private key, totally insecure, for testing only!
# Base-64-encoded, zlib-compressed PEM data (which is itself base-64 encoded...)
defaultprivkeydata = '''
    eJxtk7eSo0AABXO+YnPVFoxAmGADnBB+ECAQGd4jvPv627v4On1Z1+vv7184UZKNr6fNfsGn/GId
    8UsV33+Hb0SXZd7PZY5lVS63+Cpl7FtlH1PV3bwljQbp0nkua53RQCYxTSxMWsX1lKgwP8AMBw+p
    TnmwitoQXpQ+MCzaMWnLE61PzloeOWMI/c+HxncrJ27YTBz8MRxqD20MMHfTJfocKdQ60KDsw6Gc
    pbAxBQrW6ePqsWlBT7xvODw+iOIHAEhP5eKn8ioRGCuZqSULrMVyCPuROFZWRsOOgve4MaSWOWKN
    65f5fCSaQikUnhtDN1Jg8Bu/JA/cKaiYssOgzPuamRHHfknyrb3od4HOMI9+vpX32z0Tuc0acr37
    vMJCahtsLVwkYlwfNYAlLfmbIWQuWm0kUpifh98eRe7yDgY2OQG5TVYo7PggXC1mltY9PwRsUW7B
    6at0z9Yie336tRgoii5SGsK+b0aS7UG9T60WnccaeBdrZcCW35l9rE82vUe5G54HB+xJNh1cA53m
    9XHkeF4EAYXsRrRYh6e4m8KxuqDKTEOmkdRCRZMyPvjcnkMubabJVUuoEdDx5GoUxAIvVQFToDUj
    hydhgn4PNLW/+qUwVC/afd1D3WhK87qeWEzovCUtVOehKvNi1suamBPdAyom0GqNRoRsFgEzn95l
    w+WdJM+8rqy2dJ5oSF7hQB/4S7XRBygC3I3glmVAKrM4jJVHUvOWxR8I0On45fz+ryUBYPKChHMs
    gAzt+JCiV8XyS3N4FLdlqTT1OuD6tG3H6TbdpBeA2cIeqdOGe9syWZSe4Ipc2Tyo/a/pgffQiNwn
    Zgjf84I5GbFXdRK7fZ7xBDZWfsJ+UjA6CC6+ijLTZsrQ0O7ELh43yg46RdCVoPUQrY/Y0K6395/2
    NlP5zw/yLyHREP6f1h9R+B6O'''

# Python logo as a base-64-encoded, zlib-compressed SVG XML data
defaulticondata = '''
    eJyFVF1v20YQfC/Q/3Bl0be74+3tfQZRA1h24gJJa6COij66EiMSdSVDUiW3vz5zRyp2CgMVLHrJ
    /ZjZmRNfv3n8614cu91+2G5mDWnTiG6z3K6GzXrWfLx9q1Lz5sdvv3n93eUv89vfb67E/rgWNx8v
    3v80F41q29943raXt5fi18U7QZrE7bD5p22vfm5E0x8OD6/a9nQ66RPr7W7dvtvdPfTDct+iukV1
    6WwxkUgd0KdXh1VT0ArIH3f77ma3/TTcd7OmZJvnPKkRYL7Zv9qD6wO+szPc+YHeb//eLbtPwO30
    pjuMWFNSmYo1zpi9wNQaYwqzM8zj/bD586VCyjm3NduI07A69GBnzA+N6Lth3R/Od8ehO11sH2eN
    EUYEh7+66LpcHu4OvcCe97Pmew4hZ9eI1az5QEln5yVZ7YxfGsXaJyeNzoGU156dDNqGpIJ2gZes
    g2HsFZhk0tZaxJFKt8cTI4RAiTOMAT7Y2pola5PjFNcxC+u05aVBxmG01TERMkzqXMR0bb22ZJcK
    pd5Ko6JOHNERbJjiqKP1R69DdD3K2OSCjw2CwwZgH0PA8GAL++DLlbGjIm2NRUN2CMlTGVd2Vlgj
    EETQOSfkyUaJa5oaZUHlMe6djoavmbRLR0zxsWBfj2IuRjHffyXtv037Xxuu4oVnM9rgnDZkpTfa
    ulSVgQ1YhYik15zTkzRlBcC7LElz8CpBaliATYJ6bgS6mbwqVgY1mmh15qzOhmLSgpN21lbfnbHS
    FmFLir7YztSPU5fQIkKmqkMsMpswxUVAeyznhQKkwekaT0JwCfXgHyJGR5qmTlvAB89QOOdCH/bh
    SEVbECYjilOoZh1jqka6sVM9m9KPN5MVxYkE7InyYtTzBe3f1s+ovbXaRKhJQIASVLbHS8plYDJw
    cPVjWChnD4K4q/obn6a45svWpu7iVUm6+pjVUwnPLUy1SRLrnFieseGM9fI5k/8hzQFuZOkBwzyy
    xhGtoJWre6LtKu080q41YYxq8olzrpypPo7qS0Wcc8TPFYcTZ0SecctKVn7FYmLc1vdNea/h/2dD
    N2YO'''

# "Python for S60" compiled resource as a base-64-encoded, zlib-compressed data
pythons60rscdata = '''
    eJzL9pIXYACCVnFWhouea4oYtRk4QHwWIGYMqAgEs6E0CEgxnOGAsRnYGRlYgXKcnK4VJal5xZn5
    eYJg8f9AwDDkgQSDAhDaMCQypDPkMhQzVDLUM7QydDNMZJjOMJdhMcNKhvUMWxl2MxxkOM5wluEy
    w02G+wxPGV4zfGT4zvCXgZmRk5GfUZRRmhEAjnEjdg=='''
