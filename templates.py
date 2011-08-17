# Program TEMPLATES          
def raxml_template():
    seqtype = "PROT" 
    model = "JTT"
    cpus = 8
    tree_name = "tree_name" 
    outdir = "/home/jhuerta/"
    alg_path = "/home/jhuerta/alg.fasta"
    partitions_file = None
    args = {'-f': "d", # Normal ML algorithm 
            '-T': '%d' %cpus, 
            '-m': '%sGAMMA%s' %(seqtype, model),
            '-s': alg_path,
            '-n': tree_name, 
            '-g': outdir,
            '-q': partitions_file,
            }
    return args

def muscle_template():
    msf_file = "/path/to/infile"
    out_file = "/path/to/alg"
    bin = "muscle"
    args = {'-in': msf_file,
            '-out': out_file
            }
    return args

def phyml_template():
    seqtype = "aa"
    alg_file = "path/to"
    model = "JTT"
    optimization = "tlr"  #optimize tree topology (t), branch length
                          #(l) rate parameters (r)
    categories = "4"
    args = {"--datatype": stype,
            "--input": alg_file,
            "--bootstrap": "0",
            "-f": "m", # char freq (m)odel or (e)stimated
            "--pinv": "e",
            "--alpha": "e",
            "-o": optimization,
            "--nclasses": categories,
            "--model": model,
            "--quiet"
            }
    return args

def bionj_template():
    seqtype = "aa"
    alg_file = "path/to"
    model = "JTT"
    categories = "4"
    args = {"--datatype": stype,
            "--input": alg_file,
            "--bootstrap": "0",
            "-f": "m", # char freq (m)odel or (e)stimated
            "--pinv": "e",
            "--alpha": "e",
            "-o": "lr",
            "--nclasses": categories,
            "--model": model,
            "--quiet"
            }
    return args
