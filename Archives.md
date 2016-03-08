# Archives #

Back to [main page](Welcome.md).


# Download #

Ensymble pre-[squeezed](http://effbot.org/zone/squeeze.htm) versions are ready to use. Just copy the file to a suitable place (on command search path) and start using it!


## Older versions ##

v0.27 2008-06-30

  * Source: [ensymble-0.27.tar.gz](http://ensymble.googlecode.com/files/ensymble-0.27.tar.gz) (96 kB)
  * Pre-squeezed version for Python v2.2: [ensymble\_python2.2-0.27.py](http://ensymble.googlecode.com/files/ensymble_python2.2-0.27.py) (94 kB)
  * Pre-squeezed version for Python v2.3: [ensymble\_python2.3-0.27.py](http://ensymble.googlecode.com/files/ensymble_python2.3-0.27.py) (83 kB)
  * Pre-squeezed version for Python v2.4: [ensymble\_python2.4-0.27.py](http://ensymble.googlecode.com/files/ensymble_python2.4-0.27.py) (80 kB)
  * Pre-squeezed version for Python v2.5: [ensymble\_python2.5-0.27.py](http://ensymble.googlecode.com/files/ensymble_python2.5-0.27.py) (78 kB)
  * Documentation: [README-0.27.txt](http://ensymble.googlecode.com/files/README-0.27.txt) (42 kB)

Changes:

  * Implemented --heapsize option for the py2sis and altere32 commands. Sometimes the default heap maximum limit of one megabyte is not enough, for example when handling large pictures from the built-in camera.
  * Implemented an --extrasdir option for the py2sis command. It allows flexible placement of extra files, just like the simplesis command does.
  * Added support for PKCS#8 format private keys. Some people have received these types of keys from Symbian.


v0.26 2008-01-27

  * Source: ensymble-0.26.tar.gz (92 kB)
  * Pre-squeezed version for Python v2.2: ensymble\_python2.2-0.26.py (91 kB)
  * Pre-squeezed version for Python v2.3: ensymble\_python2.3-0.26.py (81 kB)
  * Pre-squeezed version for Python v2.4: ensymble\_python2.4-0.26.py (78 kB)
  * Pre-squeezed version for Python v2.5: ensymble\_python2.5-0.26.py (76 kB)
  * Documentation: README-0.26.txt (40 kB)

Changes:

  * Incorporated a --runinstall option for the py2sis command, developed by Jari Kirma.
  * Commands mergesis and signsis no longer choke on extra bytes in input SIS files, the bytes are simply discarded. PyS60 v1.4.2 SIS file from Nokia contains 1272 extra bytes. Purpose of these bytes is not known at this time and removing them seems to have no effect.


v0.25 2007-12-15

  * Source: ensymble-0.25.tar.gz (92 kB)
  * Pre-squeezed version for Python v2.2: ensymble\_python2.2-0.25.py (90 kB)
  * Pre-squeezed version for Python v2.3: ensymble\_python2.3-0.25.py (80 kB)
  * Pre-squeezed version for Python v2.4: ensymble\_python2.4-0.25.py (78 kB)
  * Pre-squeezed version for Python v2.5: ensymble\_python2.5-0.25.py (76 kB)
  * Documentation: README-0.25.txt (39 kB)

Changes:

  * Added --drive option to py2sis and simplesis commands, for setting the installation drive.
  * Added --vendor option for the simplesis command, like already implemented for the py2sis command.
  * The OpenSSL command line tool can reside in the same directory as Ensymble now. This allows simpler Windows installation.
  * Prevent leaving zero-byte output files behind when no OpenSSL tool is found.
  * Made it possible to use numeric capability bitmasks.
  * Rewrote installation instructions to better take Windows users into account.


v0.24 2007-10-18

  * Source: ensymble-0.24.tar.gz (92 kB)
  * Pre-squeezed version for Python v2.2: ensymble\_python2.2-0.24.py (90 kB)
  * Pre-squeezed version for Python v2.3: ensymble\_python2.3-0.24.py (80 kB)
  * Pre-squeezed version for Python v2.4: ensymble\_python2.4-0.24.py (77 kB)
  * Pre-squeezed version for Python v2.5: ensymble\_python2.5-0.24.py (75 kB)
  * Documentation: README-0.24.txt (37 kB)

Changes:

  * Added --autostart option to the py2sis command, like in the official py2sis.
  * Added --vendor option to the py2sis command for setting the vendor name shown during SIS installation.
  * Added infoe32 command for inspecting Symbian OS e32image files (EXEs, DLLs), contributed by [Martin Storsjö](http://www.martin.st/software/).


v0.23 2007-07-16

  * Source: ensymble-0.23.tar.gz (89 kB)
  * Pre-squeezed version for Python v2.2: ensymble\_python2.2-0.23.py (88 kB)
  * Pre-squeezed version for Python v2.3: ensymble\_python2.3-0.23.py (78 kB)
  * Pre-squeezed version for Python v2.4: ensymble\_python2.4-0.23.py (76 kB)
  * Pre-squeezed version for Python v2.5: ensymble\_python2.5-0.23.py (75 kB)
  * Documentation: README-0.23.txt (35 kB)

Changes:

  * Python for S60 changed its UID due to Nokia finally signing it, so Ensymble uses the new UID from now on as an installation time dependency.
  * Clarified README in using embedded version and UID strings with the py2sis command.


v0.22 2007-02-08

  * Source: ensymble-0.22.tar.gz (84 kB)
  * Pre-squeezed version for Python v2.2: ensymble\_python2.2-0.22.py (88 kB)
  * Pre-squeezed version for Python v2.3: ensymble\_python2.3-0.22.py (78 kB)
  * Pre-squeezed version for Python v2.4: ensymble\_python2.4-0.22.py (76 kB)
  * Pre-squeezed version for Python v2.5: ensymble\_python2.5-0.22.py (75 kB)
  * Documentation: README-0.22.txt (34 kB)

Changes:

  * Added simplesis command for creating a SIS package out of a directory structure.
  * Added maximum file size sanity check for py2sis command.


v0.21 2007-02-01

  * Source: ensymble-0.21.tar.gz (84 kB)
  * Pre-squeezed version for Python v2.2: ensymble\_python2.2-0.21.py (81 kB)
  * Pre-squeezed version for Python v2.3: ensymble\_python2.3-0.21.py (72 kB)
  * Pre-squeezed version for Python v2.4: ensymble\_python2.4-0.21.py (70 kB)
  * Pre-squeezed version for Python v2.5: ensymble\_python2.5-0.21.py (69 kB)
  * Documentation: README-0.21.txt (24 kB)

Changes:

  * Added mergesis command for combining several SIS files into one.


v0.20 2007-01-01

  * Source: ensymble-0.20.tar.gz (84 kB)
  * Pre-squeezed version for Python v2.2: ensymble\_python2.2-0.20.py (77 kB)
  * Pre-squeezed version for Python v2.3: ensymble\_python2.3-0.20.py (69 kB)
  * Pre-squeezed version for Python v2.4: ensymble\_python2.4-0.20.py (67 kB)
  * Pre-squeezed version for Python v2.5: ensymble\_python2.5-0.20.py (66 kB)
  * Documentation: README-0.20.txt (24 kB)

Changes:

  * Revamped documentation. Now every command and option is explained.
  * Added signsis command for (re-)signing SIS files.
  * Added altere32 command for altering pre-compiled Symbian EXEs and DLLs.
  * Implemented text file option for py2sis command. This is a requirement of Symbian's [Freeware Route to Market](https://www.symbiansigned.com/app/page/overview/freewareFaq).
  * Made py2sis language option more robust against mistyped language codes.
  * Miscellaneous clean-ups


v0.15 2006-11-18

  * Source: ensymble-0.15.tar.gz (72 kB)
  * Pre-squeezed version for Python v2.2: ensymble\_python2.2-0.15.py (66 kB)
  * Pre-squeezed version for Python v2.3: ensymble\_python2.3-0.15.py (60 kB)
  * Pre-squeezed version for Python v2.4: ensymble\_python2.4-0.15.py (58 kB)
  * Pre-squeezed version for Python v2.5: ensymble\_python2.5-0.15.py (57 kB)
  * Documentation (very incomplete): README-0.15.txt (9 kB)

Changes:

  * Rewrote certificate to binary conversion. Fixes certificate problems on Windows. Some generated SIS files were not installable.
  * Removed line feed after pass phrase for OpenSSL. It caused "wrong pass phrase" errors on Windows.


v0.14 2006-11-12

  * Source: ensymble-0.14.tar.gz (71 kB)
  * Pre-squeezed version for Python v2.2: ensymble\_python2.2-0.14.py (66 kB)
  * Pre-squeezed version for Python v2.3: ensymble\_python2.3-0.14.py (60 kB)
  * Pre-squeezed version for Python v2.4: ensymble\_python2.4-0.14.py (58 kB)
  * Pre-squeezed version for Python v2.5: ensymble\_python2.5-0.14.py (57 kB)
  * Documentation (very incomplete): README-0.14.txt (8 kB)

Changes:

  * Modified the generated SIS format a bit, to be compatible with Windows signsis.exe.
  * Test UIDs use lower case appname now, due to Symbian OS being case insensitive. What this means is that programs "test.py" and "TeSt.pY" now get the same (automatically generated) test UID.
  * Added support for signature chains. Signature chains are used by Symbian Signed (DevCerts and other certificates).


Fourth public preview release: v0.13 2006-10-06

  * Source: ensymble-0.13.tar.gz (71 kB)
  * Pre-squeezed version for Python v2.2: ensymble\_python2.2-0.13.py (65 kB)
  * Pre-squeezed version for Python v2.3: ensymble\_python2.3-0.13.py (59 kB)
  * Pre-squeezed version for Python v2.4: ensymble\_python2.4-0.13.py (57 kB)
  * Pre-squeezed version for Python v2.5: ensymble\_python2.5-0.13.py (55 kB)
  * Documentation (very incomplete): README-0.13.txt (8 kB)

Changes:

  * OpenSSL invocation uses absolute paths now. This corrects problems with Windows XP Pro.


Third public preview release: v0.12 2006-10-05

  * Source: ensymble-0.12.tar.gz (71 kB)
  * Pre-squeezed version for Python v2.2: ensymble\_python2.2-0.12.py (66 kB)
  * Pre-squeezed version for Python v2.3: ensymble\_python2.3-0.12.py (59 kB)
  * Pre-squeezed version for Python v2.4: ensymble\_python2.4-0.12.py (58 kB)
  * Pre-squeezed version for Python v2.5: ensymble\_python2.5-0.12.py (56 kB)
  * Documentation (very incomplete): README-0.12.txt (8 kB)

Changes:

  * Implemented automatic test UID generation for the py2sis command.
  * Added warning message for UIDs in the protected range.
  * Changed OpenSSL path detection to be carried out only on demand.
  * Added debug messages for troubleshooting OpenSSL-related problems.
  * Miscellaneous clean-ups


Second public preview release: v0.11 2006-09-26

  * Source: ensymble-0.11.tar.gz (71 kB)
  * Pre-squeezed version for Python v2.2: ensymble\_python2.2-0.11.py (65 kB)
  * Pre-squeezed version for Python v2.3: ensymble\_python2.3-0.11.py (58 kB)
  * Pre-squeezed version for Python v2.4: ensymble\_python2.4-0.11.py (56 kB)
  * Pre-squeezed version for Python v2.5: ensymble\_python2.5-0.11.py (55 kB)
  * Documentation (very incomplete): README-0.11.txt (7 kB)

Changes:

  * Made the default certificate a bit more anonymous.
  * Added Windows (NT/2000/XP) support.


First public preview release: v0.10 2006-09-24

  * Source: ensymble-0.10.tar.gz (116 kB)


---

Copyright © 2006, 2007, 2008, 2009 Jussi Ylänen