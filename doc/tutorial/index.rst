Overview
************

NPR Usage
*********************

Genetree workflow
===================

The genetree mode allows to run a phylogenetic analyses of a given
group of sequences, typically a gene family. Only the FASTA file
containing the amino acid or nucleotide sequences will be necessary to
start the analysis.

If NPR capabilities are enabled, both amino acid and nucleotide
sequences can be provided at the same time, thus delegating the use of
one or another to the NPR criteria (i.e. Switch to nucleotides when
amino acid sequences are too similar).

Example
---------

   npr -m genetree -a AAseqs.fasta -n NTseqs.fasta -o genetree_results/ -c MyConfig.cfg -x 


Species tree workflow
========================


This execution mode allows to reconstruct species phylogenies using a
gene concatenation approach. In order to start an analysis, a list of
one-to-one orthologous gene pairs will be necessary.

Orthologous pairs must be provided as a tab delimited text file in
which each line represents a pair.

  :: 
      geneA_sp1     geneA_sp2
      geneB_sp1     geneB_sp2 
      geneC_sp1     geneD_sp2
      geneB_sp1     geneC_sp3

Example
----------

   npr -m sptree -a AAseqs.fasta --ortho-pairs orthologs.tab -o genetree_results/ -c MyConfig.cfg -x 
      
By default, underscore "_" is used as delimiter between gene and
species names. However it can be changed through the
"--spname-delimiter" option.

Additionally, a fasta file containing the sequences of all sequences
referred in the orthologs file must be provided using the -a or -n
options.

Configuring a workflow 
=========================





Enabling Multi-threading
===============================







