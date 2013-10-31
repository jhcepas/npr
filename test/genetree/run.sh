#!/bin/sh 

# This is a test NPR script used to compile the portable package with
# CDE.

DN="$(dirname "$(readlink -f "${0}")")"
echo "Exploring NPR dir ..." $DN/../../
# This is a trick to ensure all npr files are included in the pkg. CDE
# will include any file that has been accessed, so I stat every single
# file
find $DN/../../* -exec stat {} \; |wc -l  

# Now run a real example, so I can grab all dependencies and put them
# in the CDE pkg
$DN/../../npr -w genetree -a $DN/Phy00085K5_HUMAN.alg.raw.fasta --dealign -c $DN/workflow.cfg -o /tmp/tmpresult -x -v4 -t1 --clearall --override -t1 --launch_time 1 -m2 --compress
$DN/../../nprdump -a /tmp/tmpresult/
#$DN/../../nprtop /tmp/tmpresult/
#$DN/../../nprview /tmp/tmpresult/final_tree.nw 

# pack all binaries
for cmd in /bin/*; do ldd $cmd >/dev/null; done
for cmd in /usr/bin/*; do ldd $cmd >/dev/null; done

# Ensure this commands are also included
time tar -jcf test.tar.bz2  $DN/Phy0007XAR_HUMAN.msf.aa
date
gzip
bzip2
ls
cp
ln 
du
cp
rm
sqlite3 --version