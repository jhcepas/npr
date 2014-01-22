
ETE-NPR requires many external programs to be properly configured and installed
in your system. All dependencies are Unix compatible (Linux and OSX) and could
be installed manually. 

However, for portability and reproducibility reasons, we recommend the use of
one of the available portable packages, which encapsulate all the necessary
tools and libraries necessary. Note that portable packages are much bigger than
the the application itself, as they contain a whole distribution of properly
configured software and working environment.


Linux Portable package (recommended for HPC environments)
===============================================================

This portable package should work on any modern linux distribution (kernel >=
2.6.28) and does not require installation nor root privileges. Just download the
latest package, decompress, and call any of the npr programs included in the
root folder.

1. 32-bits portable version http://etetoolkit.org/ETE-NPR/downloads/npr-linux-x32-portable.latest
1. 64-bits portable version http://etetoolkit.org/ETE-NPR/downloads/npr-linux-x64-portable.latest

Old version can be found at http://npr.cgenomics.org/downloads/



OSX portable (virtual) package
===================================

Although ETE-NPR supports native execution under OSX environments, it may
require many dependencies and libraries to be installed (see the Native
Installation section). More importantly, the versions of external software
required may differ from the ones tested with ETE-NPR. Therefore, a lightweight
virtual environment is provided transparent execution of the application without
changing your local environment.

Only two steps are required: 

1. Download and install VirtualBox for MacOS. Note that no extra configuration
steps are required. This portable package just needs virtualbox libraries and
binaries available in the system.
2. Download and decompress the latest MacOS portable package. 

To use it, change to the etenpr directory and executes the npr commands from
inside that directory.

.. warning: 

   Note that ETE-NPR environment provided along with this package will be
   restricted to the userdata/ folder contained in the package directory. All
   your input and output data must reside there, meaning that paths should all
   be relative paths 


Native Installation
===================================

$ git clone https://github.com/jhcepas/npr.git
$ cd npr/
$ wget http://etetoolkit.org/ETE-NPR/ext_apps/ext_apps-source-latest.tgz 
$ tar -zxf ext_apps-source-latest.tgz 
$ cd ext_apps/ && sh ./compile_all.sh




















Download and install ete dependencies: 
-----------------------------------------

Download latest stable sources from: 
-----------------------------------------

Download external software from into ETE-NPR directory: 
--------------------------------------------------------

Compile external software by running compile.sh
--------------------------------------------------





