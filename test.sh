rm /tmp/npr_test/ -rf
./npr -a examples/Phy0008D92_HUMAN.msf.aa -n examples/Phy0008D92_HUMAN.msf.nt -c ./genetree.cfg -o /tmp/npr_test/ -rename $@
