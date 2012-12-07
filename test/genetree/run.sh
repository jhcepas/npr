#!/bin/sh 

# This is a test NPR script used to compile the portable package with
# CDE.

DN="$(dirname "$(readlink -f "${0}")")"
echo "Exploring NPR dir ..."
# This is a trick to ensure all npr files are included in the pkg. CDE
# will include any file that has been accessed, so I stat every single
# file
find $DN/../../ -exec stat {} \; |wc -l  
# Now run a real example, so I can grab all dependencies and put them
# in the CDE pkg
$DN/../../npr -w genetree -c $DN/workflow.cfg -a $DN/Phy0007XAR_HUMAN.msf.aa -o /tmp/tmpresult -x -v4 -t1 --nodetach
