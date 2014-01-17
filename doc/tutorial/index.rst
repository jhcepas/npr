ETE-NPR Tutorial
*******************

ETE-NPR is a Python program that encapsulates all the necessary software and
methods to reconstruct phylogenetic trees starting from a single FASTA file. It
provides a convenient interface based on a single configuration file, in which a
complex phylogenetic workflow can be conveniently prototyped. 

In addition, ETE-NPR implements the Nested Phylogenetic Reconstruction (NPR)
algorithm, by which nodes in a phylogenetic tree can be hierarchically revisited
through several iterations in order to maximize the resolution of internal
nodes.

ETE-NPR can be used as a high level wrapper for many standard phylogenetic
reconstruction workflows, with or without NPR capabilities, including gene
familiy tree reconstruction or super-matrix species trees.

If you use this program for published work, please cite the following reference:

 1. Huerta-Cepas J, Bork P and Gabaldón T. *ETE-NPR: a portable application
    for nested phylogenetic reconstruction and workflow design.* (submitted)

If you are also using the NPR strategy, please cite: 

 2. Huerta-Cepas J, Marcet-Houben M, and Gabaldón T. *Nested
    Phylogenetic Reconstruction: Scalable resolution in a growing Tree
    of Life.* (submitted)

Contents:

.. toctree::
   :maxdepth: 2

   workflow_design
   family_tree_workflow
   supermatrix_workflow
   multithreading
   nprtop
   nprdump

   
