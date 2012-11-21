Overview
************

Nested Phylogenetic Reconstruction (NPR) is a novel methodology that
addresses phylogenetic inference as an iterative process by which the
resolution of internal nodes is gradually refined from root to leaves
in an automatic way.

The following documentation refers to the `npr` program, a command
line application allowing to apply the NPR strategy on top of variety
of predefined phylogenetic workflows.

A single configuration file is used by ttrough's` program to define
both NPR parameters and `workflow design`_.


If you use this program for published work, please cite: 

* Huerta-Cepas J and Gabaldón T. *ETE-NPR: a portable application for
  nested phylogenetic reconstruction and workflow design.*

* Huerta-Cepas J, Marcet-Houben M, and Gabaldón T. *Nested Phylogenetic
  Reconstruction: Scalable resolution in a growing Tree of Life.*

.. [workflow design] Workflow design 

Workflow Design
******************

Workflows are defined in the `[sptree]` and `[genetree]` sections of
the main config file. Every column within such sections will define
the details of a precise workflow (i.e. software used) and the
conditions under which such a workflow should be used. 

In the following example, we define two possible workflows: 

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

       # Workflow conditions        
       max_seqs             =   500,             1000,          
       max_seq_similarity   =   1.0,             1.0,           
       switch_aa_similarity =   0.95,            0.95,          
       min_branch_support   =   1.0,             1.0,           
                                                                
       # Workflow design                                        
       aa_aligner           =   @meta_aligner,   @clustalo, 
       aa_alg_cleaner       =   @trimal,         none,       
       aa_model_tester      =   @prottest,       none,     
       aa_tree_builder      =   @phyml,          @phyml,        
                                                                
       nt_aligner           =   @muscle,         none,       
       nt_alg_cleaner       =   @trimal,         none,       
       nt_model_tester      =   none,            none,          
       nt_tree_builder      =   @phyml,          none,        
                                                                
       outgroup_size        =   4,               4,             
       outgroup_dist        =   min,             min,           
       outgroup_min_support =   0.99,            0.99,          
       outgroup_topodist    =   False,           False,         
       outgroup_policy      =   node,            node,          

Configuring external software
===================================

The application required by a given workflow are actually referred in
the config file by providing a code name starting with a "@"
symbol. Each of such names point to its corresponding section in the
same config file (i.e. `@raxml` will point to the `[raxml]`
section). If two different uses of the same application are necessary
within the same npr configuration, new application blocks could be
created. In the following example, the `phyml` program is executed in
two different ways, each referred in a different workflow.


.. code-block:: ini

    # Set of sequences larger than 500 will be analyzed using
    # phyml_bionj mode, while full phyml will be used for smaller
    # sets.

    [genetree]
       # Workflow conditions        
       max_seqs             =   500,             1000,          
       max_seq_similarity   =   1.0,             1.0,           
       switch_aa_similarity =   0.95,            0.95,          
       min_branch_support   =   1.0,             1.0,           
                                                                
       # Workflow design                                        
       aa_aligner           =   @meta_aligner,   @clustalo, 
       aa_alg_cleaner       =   @trimal,         @trimal,       
       aa_model_tester      =   @prottest,       none,     
       aa_tree_builder      =   @phyml_ml,       @phyml_bionj,     
                                                                
       nt_aligner           =   @muscle,         none,       
       nt_alg_cleaner       =   @trimal,         none,       
       nt_model_tester      =   none,            none,          
       nt_tree_builder      =   @phyml,          none,        
     
     
    [phyml_bionj]
      _app = phyml
      _class = Phyml
      _aa_model = JTT # AA model used if no model selection is performed
      _nt_model = GTR # Nt model used if no model selection is performed
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
      _class = Phyml
      _aa_model = JTT # AA model used if no model selection is performed
      _nt_model = GTR # Nt model used if no model selection is performed
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


In situ versus Remote execution
****************************************

`npr` acts both as a pipeline director and as application
launcher. All tasks belonging to the same workflow will be processed
in a hierarchical way, thus meeting cross dependencies when necessary
(i.e. Certain tasks will not start until other has successfully
finished).

By default, all applications will be launched *in situ*, meaning that
they will run at the same computer where the `npr` command was
started.

This behavior can be changed for all or certain tasks, allowing three
possible execution modes:

1) `in-situ` (default)
2) grid-engine (submit the task to a cluster using grid engine system)
3) execution-hook (process the command to be launched in custom manner)

.. code-block:: ini

   [grid-engine]
   raxml-pthreads = qsub_1

   [execution-hook]
   phyml = process_phyml_hook

   [qsub_1]
   CELL = "cgenomics"
   -q = long
   -pe = smp 8 
  


Enabling Parallel computation
********************************

Several layers of parallel computation are available


Multi CPU Task distribution
==============================

Many tasks in a phylogenetic workflow depend on each other. Other,
however, could be computed in parallel. ETE-NPR is fully aware of the
task tree of dependencies, meaning that, when more than 1 CPU is
available, independent tasks will be launched in parallel.

In example, if 5 evolutionary models are to be tested for the same
alignment, they will be launched at the same time as soon as 5 CPU
slots are available.

The maximum number of CPU slots can be defined in the command line
through the "-m" parameter.

.. code-block:: guess

      npr -m genetree -a AAseqs.fasta -o genetree_results/ -c MyConfig.cfg -x -m 16


Multi-threading
================

Certain steps of phylogenetic workflows may involve programs with
multi-threading capabilities (i.e. parallel computing). The maximum
number of threads per process can be defined in the **threading**
section of the config file. Multi-threading applications will consume
several CPU slots.


In the following example, raxml will be allowed to run using 16
threads, mattf using 4 and FastTree 3:

.. code-block:: ini

     [threading]

     raxml-pthreads = 16
     mafft = 4
     fasttree = 3


Note that: 

i) if the number of CPUs available is **higher** than the threading
limits, other task will be able to run in parallel with the
multi-threading application.

ii) if the number if CPUs available is **lower** than the threading
limits, applications will stick to the minimum number.


Cluster-based Task distribution 
================================

Alternatively, heavy tasks could be submitted to a remote
cluster. Currently, only `Grid Engine` environments are fully
integrated, bindings to any other system can be easily implemented
through a `task execution hook function`.


Grid Engine
-----------------

Task execution hook function
----------------------------------

.. code-block:: python

  def task_execution_hook(command, config):
      print commands







Genetree workflow
*********************

The `genetree` mode allows to run a phylogenetic analysis for a given
group of sequences, typically a gene family. Only a FASTA file,
containing amino acid or nucleotide sequences, will be necessary to
start the analysis.

Both amino acid and nucleotide sequences could be provided at the same
time. In such a case, the application will choose the more suitable
set according to the **switch_aa_similarity** parameter defined in the
config file. 

.. code-block:: sh

   npr -m genetree -a AAseqs.fasta -n NTseqs.fasta -o genetree_results/ -c MyConfig.cfg -x 


Species tree workflow
*************************

`sptree` execution mode allows to reconstruct species phylogenies using a
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

Configuring a workflow 
=========================



