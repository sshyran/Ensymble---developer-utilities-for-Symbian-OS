#!/bin/sh

if test -z "$1"; then
  echo "install.sh targetpath"
  exit 1
fi

squeeze/squeeze.py -1 -o ensymble -b cmdmain cmdmain.py cmd_altere32.py cmd_py2sis.py cmd_signsis.py cmd_version.py cryptutil.py miffile.py rscfile.py sisfield.py sisfile.py symbianutil.py defaultcert.py
cp ensymble.py "$1"
chmod +x "$1"/ensymble.py
rm ensymble.py

echo "Ensymble command line tool installed as $1/ensymble.py"
