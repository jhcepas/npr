Running a family-tree workflow 
*************************************

The `familytree` mode allows to run a phylogenetic analysis for a
given group of sequences, typically a gene family. Only a FASTA file,
containing amino acid or nucleotide sequences, will be necessary to
start the analysis.

Both amino acid and nucleotide sequences could be provided at the same
time. In such a case, the application will choose the more suitable
set according to the **switch_aa_similarity** parameter defined in the
config file. 

.. code-block:: sh

   npr -m genetree -a AAseqs.fasta -n NTseqs.fasta -o genetree_results/ -c MyConfig.cfg -x 

Available templates
=======================

phylomedb pipeline
--------------------





