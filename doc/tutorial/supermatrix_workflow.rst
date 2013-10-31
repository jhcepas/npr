Running a supermatrix based workflow 
**************************************

`supermatrix` execution mode allows to reconstruct species phylogenies using a
gene a concatenation approach (aka. supermatrix). In order to start an analysis,
both a FASTA file and a list of precomputed Clusters of Orthologous Groups (COG)
are required.

  ::

   npr -m sptree -a AAseqs.fasta --ortho-pairs orthologs.tab -o
   genetree_results/ -c MyConfig.cfg -x
      
By default, the underscore symbol ("_") will be used to separate gene and
species names. However this can be changed through the
`--spname-delimiter` option.

Additionally, a fasta file containing the sequences of all sequences
referred in the orthologs file must be provided using the -a or -n
options.

Advantanges of NPR in the genetree workflow
===============================================



Workflow Configuration
==============================

The `supermatrix` workflow can be used to automatically select a list of COGs
containing single copy genes for the selected species, perform a family tree
analysis of each independent family, concatenate the resulting alignments a
compute a general species tree based on the concatenated orthologs.

For this reason, both the `[genetree]` and `[sptree]` sections of the config
file are necessary. The first will define how the alignment (and tree, if
required) of each COG is computed. The second describes how the supermatrix
trees is reconstructed and, if necessary, how to proceed with NPR iterations.

.. code-block:: ini

   [genetree]
   max_iters = 1                            # If higher than 1, NPR capabilities will be enabled
    
   #                        WORKFLOW-1      # Each column represent a different phylogenetic workflow 
   max_seqs             =   6,              # max number of sequences for each workflow
   max_seq_similarity   =   0.99,           # sequence similarity** (between 0 and 1) at which NPR should stop processing 
   switch_aa_similarity =   0.95,           # sequence similarity** (between 0 and 1) at which NPR should switch to nt sequences, if available
   min_branch_support   =   1.0,            # minimum support value for a node to be optimized using NPR 
   min_npr_size         =   3,              # minimum size of a node to be selected for NPR optimization
                                          
   aa_aligner           =   @dialigntx,     # what software/method should be used to reconstruct amino acid alignments
   aa_alg_cleaner       =   @trimal,        # what software/method should be used to clean amino acid alignments
   aa_model_tester      =   @prottest2,     # what method should be used to test amino acid evolutionary models
   aa_tree_builder      =   @raxml,         # what software/method should be used to reconstruct a tree based on the amino acid alignment
                                          
   nt_aligner           =   @muscle,        # what software/method should be used to reconstruct nucleotide alignments                    
   nt_alg_cleaner       =   @trimal,        # what software/method should be used to clean nucleotide alignments                          
   nt_model_tester      =   none,           # what method should be used to test nucleotide models                           
   nt_tree_builder      =   @phyml,         # what software/method should be used to reconstruct a tree based on the nucleotide alignment 
                                          
   tree_splitter        =   @splitter,      # A config block in the same file describing how NPR iterations are computed

   ** Sequence similarity refers to the average site identity for all columns in an
      alignment (gaps excluded).

  [sptree]
  max_iters = 100                                          # If higher than one, NPR iterations will be enabled
  
  #                        WORKFLOW-1        WORKFLOW-2    # Each column represent a different workflow 
  max_seqs             =   100,               500,         # Max number of sequences handled by each workflow 
  max_seq_similarity   =   1.0,               1.0,       
  min_branch_support   =   1.0,               1.0,       
  min_npr_size         =   3,                 3,         
                                                          
  cog_selector         =   @brh_cog,          @brh_cog,    # A config block in the same file describing how COGs should be selected.
  alg_concatenator     =   @alg_concat,       @alg_concat, # A config block in the same file describing how alignments should be concatenated 
                                                          
  aa_tree_builder      =   @raxml,            @fasttree,   # Software used to reconstruct the supermatrix tree based on amino acid aligments
  nt_tree_builder      =   @raxml,            @fasttree,   # Software used to reconstruct the supermatrix tree based on nucleotide aligments  
                                                          
  tree_splitter        =   @splitter,         @splitter,   # A config block in the same file describing how NPR iterations are 
   
  target_levels = chordata, metazoa, bilateria
   
  [alg_concat]
  _app = concatalg 
  _max_cogs = 10000               # Max number of COGs that should be used
  _default_aa_model = JTT         # Default amino acid model used to infer the tree in case no partitions are available for the supermatrix
  _default_nt_model = GTR         # Default nucleotide model used to infer the tree in case no partitions are available for the supermatrix
   
  [brh_cog]
  _app = cogselector
  _species_missing_factor = 0.10  # Percentage of missing species allowed when calculating single copy COG. 

Command line
=====================

Supermatrix tree reconstruction is started using the **-m genetree** option. 

.. code-block:: sh

   npr -m sptree -a AAseqs.fasta --ortho-pairs orthologs.tab -o genetree_results/ -c MyConfig.cfg -x


