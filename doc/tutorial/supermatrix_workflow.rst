Running a supermatrix based workflow 
**************************************

`supermatrix` execution mode allows to reconstruct species phylogenies using a
gene concatenation approach. In order to start an analysis, a list of
one-to-one orthologous gene pairs will be necessary.

Orthologous pairs must be provided as a tab delimited text file in
which each line represents a pair.

  :: 

      geneA_sp1     geneA_sp2
      geneB_sp1     geneB_sp2 
      geneC_sp1     geneD_sp2
      geneB_sp1     geneC_sp3

  :: 

   npr -m sptree -a AAseqs.fasta --ortho-pairs orthologs.tab -o genetree_results/ -c MyConfig.cfg -x 
      
By default, the underscore symbol ("_") will be used to separate gene
and species names. However this can be changed through the
`--spname-delimiter` option.

Additionally, a fasta file containing the sequences of all sequences
referred in the orthologs file must be provided using the -a or -n
options.

Available templates
======================

Supermatrix species tree reconstruction 
--------------------------------------------

