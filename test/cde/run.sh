#!/bin/sh 

cd /opt/npr/
./npr_update

find -exec stat {} \; | wc -l  

./npr -w phylomedb4 -a test/cde/Phy0007XAR_HUMAN.msf.aa -n test/cde/Phy0007XAR_HUMAN.msf.nt --dealign -o /tmp/tmpresult -v2 --clearall --override -t0.7 --launch_time 1 -m4 --compress
./nprdump -a /tmp/tmpresult/

# pack all binaries
for cmd in /bin/*; do ldd $cmd >/dev/null; done
for cmd in /usr/bin/*; do ldd $cmd >/dev/null; done
