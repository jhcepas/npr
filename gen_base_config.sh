python meta_workflow.py -meta  \
   'name:test_all; 
    a:muscle_default,mafft_default,mafft_einsi,mafft_linsi,mafft_ginsi,clustalo_default,meta_aligner_default,meta_aligner_trimmed; 
    r:none,trimal01,trimal02,trimal_gappyout;m:none, prottest_default;  
    t:none,fasttree_full,fasttree_default,phyml_default,raxml_default,raxml_default_bootstrap,phyml_default_bootstrap'  \
\
    'name:aligners_only; 
     a:muscle_default, mafft_default, clustalo_default, meta_aligner_default; 
     r:trimal01,trimal02,none;m:prottest_default,none;  
     t:none'  \
\
    'name:test_aligners_fasttree; 
     a:muscle_default, mafft_default, clustalo_default, meta_aligner_default; 
     r:none,trimal01;m:none;  
     t:fasttree_full'  \
\
    'name:test_aligners_raxml; 
     a:muscle_default, mafft_default, clustalo_default, meta_aligner_default; 
     r:none,trimal01;m:none;  
     t:raxml_default'  \
\
    'name:test_aligners_raxml_models; 
     a:muscle_default, mafft_default, clustalo_default, meta_aligner_default; 
     r:none,trimal01;m:none, prottest_default;  
     t:raxml_default'  \
\
    'name:test_aligners_phyml; 
     a:muscle_default, mafft_default, clustalo_default, meta_aligner_default; 
     r:none,trimal01;m:none;  
     t:phyml_default'  \
\
    'name:test_aligners_phyml_models; 
     a:muscle_default, mafft_default, clustalo_default, meta_aligner_default; 
     r:none,trimal01;m:none, prottest_default;  
     t:phyml_default'  \
\
    'name:phylomedb4; 
     a:meta_aligner_trimmed; 
     r:trimal01;m:prottest_default;  
     t:phyml_default'  \
\
    'name:eggnog41_small; 
     a:mafft_einsi; 
     r:trimal01;m:prottest_default;  
     t:phyml_default'  \
\
    'name:eggnog41_large; 
     a:clustalo_default; 
     r:trimal01;m:none;  
     t:fasttree_full'  \
\
    'name:standard_fasttree; 
     a:clustalo_default; 
     r:none;m:none;  
     t:fasttree_full'  \
\
    'name:standard_raxml; 
     a:clustalo_default; 
     r:none;m:prottest_default;  
     t:raxml_default'  \
\
    'name:standard_phyml; 
     a:clustalo_default; 
     r:none;m:prottest_default;  
     t:phyml_default'  \
\
    'name:standard_raxml_bootstrap; 
     a:clustalo_default; 
     r:none;m:prottest_default;  
     t:raxml_default_bootstrap'  \
\
    'name:standard_phyml_bootstrap; 
     a:clustalo_default; 
     r:none;m:prottest_default;  
     t:phyml_default_bootstrap'  \
\
    'name:linsi_raxml; 
     a:mafft_linsi; 
     r:trimal01;
     m:none;  
     t:raxml_default'  \
\
    'name:linsi_phyml; 
     a:mafft_linsi; 
     r:trimal01;
     m:none;  
     t:phyml_default'  \
\
    'name:linsi_phyml_bootstrap; 
     a:mafft_linsi; 
     r:trimal01;
     m:none;  
     t:phyml_default_bootstrap'  \
\
    'name:linsi_fasttree; 
     a:mafft_linsi; 
     r:none;m:none;  
     t:fasttree_full'  \
\
     -c apps.cfg



     
