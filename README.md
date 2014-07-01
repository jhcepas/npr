This document describes how to install ETE-NPR from sources in a Linux
environment. Note that the recomended approach for most of the users is to use
the portable or virtual package available at http://etetoolkit.org/ete_npr.

However, building ETE-NPR from sources will provide a better performance than
the portable packages.

# 0. Clone this repository
```sh
  $ git clone  http://github.com/jhcepas/npr.git   
```

# 1. Install dependencies
```
  python
  python-numpy
  python-qt4 (optional, required for image generation)
  python-lxml (optional)
  python-mysqldb (optional) 
```

You will need also basic tools for compiling (gcc, g++). As an examples, the
'build-essential' package (in ubuntu) should be enough. You may also need to
install 'automake' and 'autoconf'
  
Some of the external programs require special libs that might not be installed. Most commonly: 
```
   libargparse-dev
```

# 2. Download the sources for external applications

You need to clone the following repository* at the root* of the npr/ directory:
```sh
   $ cd npr/
   $ git clone http://github.com/jhcepas/ext_apps.git 
```

# 3. Compile external applications

Enter the ext_app directory and run the compile script
```sh
   $ cd npr/ext_apps/
   $ sh compile.sh all
```
# 4. Check that the applications are detected and operative
```sh
   $ cd npr/
   $ ./npr check
```


 