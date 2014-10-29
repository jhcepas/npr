# Overview 

ETE-NPR is a bioinformatics program providing a complete environment for the
execution of phylogenomic workflows, including super-matrix and family-tree
reconstruction approaches. ETE-NPR covers all necessary steps for high quality
phylogenetic reconstruction, from alignment reconstruction and model testing to
the generation of publication ready images of the produced trees and
alignments. ETE-NPR is built on top of a bunch of specialized software and comes
with a number of predefined workflows.
     
If you use ETE-NPR in a published work, please cite:
     
       Jaime Huerta-Cepas, Peer Bork and Toni Gabaldon. In preparation. 
     
(Note that a list of the external programs used to complete the necessary
computations will be also shown together with your results. They should also be
cited.)

    Homepage:   http://etetoolkit.org/ete_npr/ 
    Contact:    huerta [at] embl.de & tgabaldon [at] crg.es

# Installing from sources 

This document describes how to install ETE-NPR from sources in a Linux
environment. Note that **the recomended approach for most of the users is to use
the portable or virtual package available at http://etetoolkit.org/ete_npr**.

However, building ETE-NPR from sources will provide a better performance than
the portable packages.

## 0. Download the latest official release from github

https://github.com/jhcepas/npr/releases

## 1. Install dependencies
```
  python
  python-numpy
  python-qt4 (optional, required for image generation)
```

You will need also basic tools for compiling (gcc, g++). As an examples, the
'build-essential' package (in ubuntu) should be enough. You may also need to
install 'automake' and 'autoconf'
  
Some of the external programs require special libs that might not be installed. Most commonly: 
```
   libargparse-dev
```

## 2. Download the sources for external applications

You need to clone the following repository* at the root* of the npr/ directory:
```sh
   $ cd npr/
   $ git clone http://github.com/jhcepas/ext_apps.git 
```

## 3. Compile external applications

Enter the ext_app directory and run the compile script
```sh
   $ cd npr/ext_apps/
   $ bash compile.sh all
```

## 4. Check that the applications are detected and operative
```sh
   $ cd npr/
   $ ./npr check
```


 