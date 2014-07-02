import os
VERSION = open("VERSION").readline()
a, b, c = map(int, VERSION.split("."))

if raw_input("Say [y] to increase version number: %s: " %VERSION).strip() == "y":
    c += 1

NEW_VERSION = "%d.%d.%d" %(a, b, c)

if raw_input("Say [y] to set current commit to new version: %s: " %NEW_VERSION).strip() == "y":
    msg = raw_input("msg for the release: ")
    
    open("VERSION", "w").write(NEW_VERSION)
    os.system('date "+%F" > DATE')
    os.system("git tag -d latest_stable; git tag -d %s" %(NEW_VERSION))
    os.system("git push")
    os.system("git tag %s -m '%s' && git tag latest_stable -m '%s' && git push --tags" %(NEW_VERSION, msg, msg))

    


