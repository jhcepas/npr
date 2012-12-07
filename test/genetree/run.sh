#!/bin/sh 
DN="$(dirname "$(readlink -f "${0}")")"
rm -rf /tmp/tmpresult
$DN/../../npr -w genetree -c $DN/workflow.cfg -a $DN/Phy0007XAR_HUMAN.msf.aa -o /tmp/tmpresult -x -v4 -t1
