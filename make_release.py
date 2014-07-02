VERSION = open("VERSION").readline()
a, b, c = map(int, VERSION.split("."))
c += 1
NEW_VERSION = "%d.%d.%d" %(a, b, c)

if raw_input("Say [y] to set current commit to new version: %s" NEW_VERSION).strip() == "y":
    open("VERSION", "w").write(NEW_VERSION)
    git tag VERSION
    git tag "latest_stable"
    git push

    


