Running a family-tree workflow 
*************************************

The `genetree` mode allows to run a phylogenetic analysis for a
given group of sequences, typically a gene family. Only a FASTA file,
containing amino acid or nucleotide sequences, will be necessary to
start the analysis.

In addition, if NPR capabilities are enabled, both amino acid and nucleotide
sequences could be provided at the same time. In such a case, the application
will choose the more suitable sequence type for each internal node, according to
the similarity of sequences grouped under each specific node (i.e. when aa
sequences are identical under a terminal partition, nt sequences will be used to
refine the node)

Advantanges of NPR in the genetree workflow
===============================================

NPR allows to refine internal nodes within a tree by accommodating different
software to different clade sizes, and by re-computing multiple sequence
alignments at every level, meaning that each NPR iteration will be based on less
sequences and more evolutionary related.


Workflow Configuration
==============================

.. code-block:: ini

   [genetree]
   max_iters = 10                                               # If higher than 1, NPR capabilities will be enabled
    
   #                        WORKFLOW-1          WORKFLOW-2      # Each column represent a different phylogenetic workflow 
   max_seqs             =   6,                  8,              # max number of sequences for each workflow
   max_seq_similarity   =   0.99,               0.99,           # sequence similarity** (between 0 and 1) at which NPR should stop processing 
   switch_aa_similarity =   0.95,               0.95,           # sequence similarity** (between 0 and 1) at which NPR should switch to nt sequences, if available
   min_branch_support   =   1.0,                1.0,            # minimum support value for a node to be optimized using NPR 
   min_npr_size         =   3,                  3,              # minimum size of a node to be selected for NPR optimization
                                                           
   aa_aligner           =   @dialigntx,         @muscle,        # what software/method should be used to reconstruct amino acid alignments
   aa_alg_cleaner       =   @trimal,            none,           # what software/method should be used to clean amino acid alignments
   aa_model_tester      =   @prottest2,         @prottest,      # what method should be used to test amino acid evolutionary models
   aa_tree_builder      =   @raxml,             @raxml2,        # what software/method should be used to reconstruct a tree based on the amino acid alignment
                                                           
   nt_aligner           =   @muscle,            @muscle,        # what software/method should be used to reconstruct nucleotide alignments                    
   nt_alg_cleaner       =   @trimal,            @trimal,        # what software/method should be used to clean nucleotide alignments                          
   nt_model_tester      =   none,               none,           # what method should be used to test nucleotide models                           
   nt_tree_builder      =   @phyml,             @raxml,         # what software/method should be used to reconstruct a tree based on the nucleotide alignment 
                                                           
   tree_splitter        =   @splitter,          @splitter,      # what strategy should be used to split the tree into NPR processes

   ** Sequence similarity refers to the average site identity for all columns in an
      alignment (gaps excluded).

In plain words, WORKFLOW-1 will be used to reconstruct trees containing 6 or
less sequences only if sequence similarity is bellow 99%, if branch support is
<= 1.0 and if the target partition contains at least 3 sequences. Also, in case
of sequence similarity is higher than 95%, nucleotide sequences will be used
instead of amino acids. Regarding the phylogenetic pipeline, amino acid
alignments will be done with Dialigntx and cleaned with Trimal. Several
evolutionary models will be tested using Protest, and Raxml will be used to
compute the final ML tree. In the case nucleotide sequences are being used for
any iteration, muscle, trimal and phyml will be used, avoiding in this case
model testing steps.

Command line
=====================

Genetree reconstruction is started using the **-m genetree** option. 

.. code-block:: sh

   npr -m genetree -a AAseqs.fasta -n NTseqs.fasta -o genetree_results/ -c MyConfig.cfg -x 
