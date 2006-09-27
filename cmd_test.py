#!/usr/bin/env python
# -*- coding: iso8859-1 -*-

##############################################################################
# cmd_test.py - Ensymble command line tool, test command
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

import sisfile
import sisfield


##############################################################################
# Help texts
##############################################################################

shorthelp = "Try to test every feature of the sisfile module"
longhelp  = '''test

Try to test every feature of the sisfile module. Creates a SIS file "test.sis".
'''


##############################################################################
# Public module-level functions
##############################################################################

def run(pgmname, argv):
    #iconmime = "image/png"
    #icondata = '''
    #iVBORw0KGgoAAAANSUhEUgAAABAAAAARBAMAAAAmgTH3AAAABGdBTUEAALGPC/xhBQAAACdQTFRF
    #WFhY////WFhY3Nzcw8PDAAAA/4AA/6hYoKCg/9yowFgAMDAwQAAAAsNBGwAAAAF0Uk5TQDY6mfYA
    #AAABYktHRACIBR1IAAAACXBIWXMAAAsQAAALEAGtI711AAAAB3RJTUUH0AoMDTY2kPKGKQAAAG1J
    #REFUeJxjYFICAwYGJmMQMCpnYDIUFBEUFC+DMsrTGJhMXFxc3MvSICLlaVlghnhZ2hqwVGVa1gaQ
    #iMTMtNUMIIb4zJlHGUBSnTNXtYJFNFc5i4IYQnucBUEMi9aOjg6IlIQgSIQ7FAwY4AAAkuAczpou
    #bUMAAAAASUVORK5CYII='''.decode("base-64")

    iconmime = "image/jpeg"
    icondata = '''
    /9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsK
    CwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQU
    FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAAgACADASIA
    AhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQA
    AAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3
    ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWm
    p6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEA
    AwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSEx
    BhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElK
    U1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3
    uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD50ooo
    r8MP9UwooooAKKKKACiiigD/2Q=='''.decode("base-64")

    # Create a bilingual SIS file with a self-signed certificate (RSA key).
    cert = file("rsatestcert.pem", "rb").read()
    key = file("rsatestkey_passphrase.pem", "rb").read()
    passphrase = u"Yöks".encode("utf-8")    # Depends on terminal encoding
    sw = sisfile.SimpleSISWriter(["FI", "EN"], ["Ohjelma", "Program"],
                                 0xf0203489L, (1, 2, 3), "Vendor",
                                 ["Kauppias FI", "Vendor EN"])
    sw.addcertificate(key, cert, passphrase)
    sw.setlogo(icondata, iconmime)
    sw.addlangdepfile([u"Gauballisd boskaa!".encode("UTF-16LE"),
                       u"Commercial crap!".encode("UTF-16LE")],
                      operation = sisfield.EOpText)
    sw.addfile("Hello, world!", "C:\\Data\\Documents\\test.txt")
    sw.addlangdepfile(["Borjensd!", "Hello, world!"],
                      "C:\\Data\\Documents\\test2.txt")
    sw.addtargetdevice(0x101f7961L, (0, 0, 0), None,
                       ["Series60ProductID", "Series60ProductID"])
    sw.adddependency(0xf0203485L, (1, 2, 3), None,
                       ["Oleellinen softa", "Crucial software"])
    sw.addproperty(0x1234, 0x4567)
    sw.addproperty(0x8901, 0x9999)
    sw.tofile("test.sis")
