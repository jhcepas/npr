Workflow Design
******************

A single configuration file is used to define both NPR parameters and workflow
design. Workflows are defined in the `[sptree]` and `[genetree]` sections of the
main config file. Every column within such sections will define the details of a
different workflows (i.e. software and parameters used) and the conditions under
which such a workflow should be used.

In the following example, two genetree workflows are defined: 

1) a faster approach to optimize partitions with 500 or more
sequences, in which clustal-omega is used to reconstruct the alignment
and fasttree to infer the tree (no model selection and no use of dna
sequences.)

2) a more complex pipeline is defined to optimize partitions with less
than 500 sequences. A `meta-aligner` plus gap trimming approach is
used to infer the alignment, prottest is used to select the best
fitting model, and phyml to infer the final tree. Also, when the
minimum sequence similarity is above 95%, DNA sequences will be used
instead of amino-acid.

.. code-block:: ini

       [genetree]

       # Workflow conditions   WORKFLOW 1       WORKFLOW 2
       max_seqs             =   500,             1000,          
       max_seq_similarity   =   1.0,             1.0,           
       switch_aa_similarity =   0.95,            0.95,          
       min_branch_support   =   1.0,             1.0,           
       min_npr_size         =   5,               5, 
                                                                
       # Workflow design                                        
       aa_aligner           =   @meta_aligner,   @clustalo, 
       aa_alg_cleaner       =   @trimal,         none,       
       aa_model_tester      =   @prottest,       none,     
       aa_tree_builder      =   @phyml2,         @phyml1,        
                                                                
       nt_aligner           =   @muscle,         none,       
       nt_alg_cleaner       =   @trimal,         none,       
       nt_model_tester      =   none,            none,          
       nt_tree_builder      =   @phyml,          none,        

       tree_splitter        =   @splitter,       @splitter

Values starting with `@` refer to specific blocks in the config file. Thus,
`@phyml2` will be translated into a phyml execution using the parameters defined
in the `[phyml2]` config block. This allows to adjust the details of the
phylogenetic workflow to different scenarios.

Configuring external software
===================================

The application required by a given workflow are actually referred in
the config file by providing a code name starting with a "@"
symbol. Each of such names point to its corresponding section in the
same config file (i.e. `@raxml` will point to the `[raxml]`
section). If two different uses of the same application are necessary
within the same workflow design, new config blocks could be
created. 

Regarding the configuration of external software, the following points
should be considered:

  1. Every application config block should contain an `_app` keyword,
     establishing the associated software.

  2. Some extra internal parameters may be available for certain software and
     they are always preceded by an underscore symbol "_"
     (i.e. _aa_model). Please refer to the comments in example config file
     provided along with this package to understand the meaning of every
     argument.

  3. Any other line in the configuration block will be taken as a program
     argument and it will be passed verbatim to the external software. Program
     options and argument must be specified in the `argument = value` format. In
     the case of *flag-based* arguments, just use an empty value
     (i.e. --no-memory-check = "").

In the following example, the `phyml` program is executed in two
different ways, each referred in a different workflow column:

.. code-block:: ini

    # Set of sequences larger than 500 will be analyzed using
    # phyml_bionj mode, while full phyml will be used for smaller
    # sets.

    [genetree]

    # Workflow conditions   WORKFLOW 1       WORKFLOW 2
    max_seqs             =   500,             1000,          
    max_seq_similarity   =   1.0,             1.0,           
    switch_aa_similarity =   0.95,            0.95,          
    min_branch_support   =   1.0,             1.0,           
    min_npr_size         =   5,               5, 
                                                             
    # Workflow design                                        
    aa_aligner           =   @meta_aligner,   @clustalo, 
    aa_alg_cleaner       =   @trimal,         none,       
    aa_model_tester      =   @prottest,       none,     
    aa_tree_builder      =   @phyml_ml,       @phyml_bionj,        
                                                             
    nt_aligner           =   @muscle,         none,       
    nt_alg_cleaner       =   @trimal,         none,       
    nt_model_tester      =   none,            none,          
    nt_tree_builder      =   @phyml,          none,        

    tree_splitter        =   @splitter,       @splitter

    
    [phyml_bionj]
      _app = phyml
      _aa_model = JTT # AA model used if no model selection is performed
      _nt_model = GTR # Nt model used if no model selection is performed

      # The following options are passed to the phyml program
      -o = lr           # Only branch length 
      --pinv = e        # Proportion of invariant sites.  Fixed value in the
                        # [0,1] range or "e" for estimated
      --alpha = e       # Gamma distribution shape parameter. fixed value or
                        # "e" for "estimated"
      --nclasses =  4   # Number of rate categories
   
      -f = m            # e: estiamte character frequencies.  m: character
                        # frequencies from model
      --bootstrap = -2  #  approximate likelihood ratio test returning
                        #  Chi2-based parametric branch supports.
     
    [phyml_ml]
      _app = phyml
      _aa_model = JTT # AA model used if no model selection is performed
      _nt_model = GTR # Nt model used if no model selection is performed

      # The following options are passed to the phyml program
      -o = tlr          # Tree optimization
      --pinv = e        # Proportion of invariant sites.  Fixed value in the
                        # [0,1] range or "e" for estimated
      --alpha = e       # Gamma distribution shape parameter. fixed value or
                        # "e" for "estimated"
      --nclasses =  4   # Number of rate categories
      -f = m            # e: estiamte character frequencies.  m: character
                        # frequencies from model
      --bootstrap = -2  #  approximate likelihood ratio test returning
                        #  Chi2-based parametric branch supports.

