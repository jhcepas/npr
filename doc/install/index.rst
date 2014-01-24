IMPORTANT NOTES REGARDING INSTALLATION
=============================================

ETE-NPR requires many external programs to be properly configured and installed
in your system. All dependencies are Unix compatible (Linux and OSX) and could
be installed manually. 

However, for portability and reproducibility reasons, we recommend the use of
one of the available portable packages, which encapsulate all the necessary
tools and libraries required to use the application. Note that portable packages
are much bigger than the application itself, as they contain a whole
distribution of properly configured software and working environment.

Linux Portable package (recommended for HPC environments and local linux installations)
=================================================================================================

This portable package should work on any modern linux distribution (kernel >=
2.6.28) and does not require installation nor root privileges. Just download the
latest `linux.HPC.portable` package from (http://etetoolkit.org/ETE-NPR/releases/linux-portable/), decompress,
and call any of the `npr` programs included in the root directory.

Virtualized portable package for Linux and MacOS (recommended for OSX)
===================================================================================================


Although ETE-NPR supports native execution under OSX environments, it may
require many dependencies and libraries to be installed (see the Native
Installation section). More importantly, the versions of external software
required may differ from the ones tested with ETE-NPR. Therefore, a lightweight
virtual environment is provided transparent execution of the application without
changing your local environment. The virtual version of ETE-NPR can run in Linux, 
MacOS hosts, and requires only VirtualBox and Vagrant to be installed as external 
dependencies.

Only two steps are required:

   .. warning::

      Installation requires several image files to be downloaded and configured
      in your system. This may take several minutes depending on your Internet
      connection and computer performance. Once installed, the application will use
      between 600M and 700M.

  1. Download and install VirtualBox from https://www.virtualbox.org/wiki/Downloads
     Note that no extra configuration steps are required. You don't need to
     execute VirtualBox, just install it.

  2. Download and install Vagrant http://www.vagrantup.com/downloads.html

  3. Download the latest `etenpr-x-x-x.virtual.linux-macos.xx.tar.gz` package from http://etetoolkit.org/ETE-NPR/releases/virtual/ and
     decompress in any local folder.

  4. Enter into the directory and execute `npr-start`.

     The first time that the command is executed, installation will be completed
     by downloading the base system and configuring the environment This may
     take several minutes to complete and requires Vagrant and VirtualBox to be
     properly installed.

     After that, and from then on, npr-start command will directly drop you
     within a ETE-NPR shell interface in which all dependencies and external
     software are already configured.

  5. Once you are inside the npr-start, you can test any of the examples
     included with the application:

     .. code:: 
    
        ETE-NPR$ cd /nprhome/npr/examples/phylomedb_tree/
        ETE-NPR$ sh run.sh


.. note::

        IMPORTANT: The ETE-NPR environment will be restricted to the `userdata/` directory
        contained in the root directory. You should copy all your input files
        into that directory before starting a npr analysis.



Native Installation
===================================

::
  
  # Get the latest stable code of ete-npr
  $ git clone https://github.com/jhcepas/npr.git


  # Enter the root directory of the application and download the latest package of software 
  $ cd npr/
  $ wget http://etetoolkit.org/ETE-NPR/releases/ext_apps/ext_apps.latest.tar.gz 
  $ tar -zxf ext_apps-source-latest.tar.gz

  # Compile all software in the package. Depending on your current system, you may need to install additional libraries, typically: libargtable and pthreads support
  $ cd ext_apps/ && sh ./compile_all.sh


  


