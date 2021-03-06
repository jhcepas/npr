import numpy
from StringIO import StringIO
import cPickle
from string import strip
from collections import defaultdict
import logging
import os
log = logging.getLogger("main")

from nprlib.master_task import CogSelectorTask
from nprlib.errors import DataError, TaskError
from nprlib.utils import (GLOBALS, print_as_table, generate_node_ids,
                          encode_seqname, md5, pjoin)
from nprlib import db

__all__ = ["CogSelector"]

class CogSelector(CogSelectorTask):
    def __init__(self, target_sp, out_sp, seqtype, conf, confname):
        self.missing_factor = float(conf[confname]["_species_missing_factor"])
        self.max_missing_factor = float(conf[confname]["_max_species_missing_factor"])
        self.cog_hard_limit = int(conf[confname]["_max_cogs"])
        node_id, clade_id = generate_node_ids(target_sp, out_sp)
        # Initialize task
        CogSelectorTask.__init__(self, node_id, "cog_selector",
                                 "MCL-COGs", None, conf[confname])

        # taskid does not depend on jobs, so I set it manually
        self.cladeid = clade_id
        self.seqtype = seqtype
        self.targets = target_sp
        self.outgroups = out_sp
        self.init()
        self.size = len(target_sp | out_sp)
        self.cog_analysis = None
        self.cogs = None
        
    def finish(self):
        def sort_cogs_by_size(c1, c2):
            '''
            sort cogs by descending size. If two cogs are the same size, sort
            them keeping first the one with the less represented
            species. Otherwise sort by sequence name sp_seqid.'''
            
            r = -1 * cmp(len(c1), len(c2))
            if r == 0:
                # finds the cog including the less represented species
                c1_repr = numpy.min([sp2cogs[_sp] for _sp, _seq in c1])
                c2_repr = numpy.min([sp2cogs[_sp] for _sp, _seq in c2])
                r = cmp(c1_repr, c2_repr)
                if r == 0:
                    return cmp(sorted(c1), sorted(c2))
                else:
                    return r
            else:
                return r

        def sort_cogs_by_sp_repr(c1, c2):
            c1_repr = numpy.min([sp2cogs[_sp] for _sp, _seq in c1])
            c2_repr = numpy.min([sp2cogs[_sp] for _sp, _seq in c2])
            r = cmp(c1_repr, c2_repr)
            if r == 0:
                r = -1 * cmp(len(c1), len(c2))
                if r == 0:
                    return cmp(sorted(c1), sorted(c2))
                else:
                    return r
            else:
                return r
            
        all_species = self.targets | self.outgroups
        # strict threshold
        #min_species = len(all_species) - int(round(self.missing_factor * len(all_species)))
        
        # Relax threshold for cog selection to ensure sames genes are always included
        min_species = len(all_species) - int(round(self.missing_factor * len(GLOBALS["target_species"])))
        min_species = max(min_species, (1-self.max_missing_factor) * len(all_species))
        
        smallest_cog, largest_cog = len(all_species), 0
        all_singletons = []
        sp2cogs = defaultdict(int)
        for cognumber, cog in enumerate(open(GLOBALS["cogs_file"])):
            sp2seqs = defaultdict(list)
            for sp, seqid in [map(strip, seq.split(GLOBALS["spname_delimiter"], 1)) for seq in cog.split("\t")]:
                sp2seqs[sp].append(seqid)
            one2one_cog = set()
            for sp, seqs in sp2seqs.iteritems():
                #if len(seqs) != 1:
                #    print sp, len(seqs)
                if sp in all_species and len(seqs) == 1:
                    sp2cogs[sp] += 1
                    one2one_cog.add((sp, seqs[0]))
            smallest_cog = min(smallest_cog, len(one2one_cog))
            largest_cog = max(largest_cog, len(one2one_cog))
            all_singletons.append(one2one_cog)
            #if len(one2one_cog) >= min_species:
            #    valid_cogs.append(one2one_cog)
            
        for sp, ncogs in sorted(sp2cogs.items(), key=lambda x: x[1], reverse=True):
            log.log(28, "% 20s  found in single copy in  % 6d (%0.1f%%) COGs " %(sp, ncogs, 100 * ncogs/float(cognumber)))

        valid_cogs = sorted([sing for sing in all_singletons if len(sing) >= min_species],
                            sort_cogs_by_size)

        log.log(28, "Largest cog size: %s. Smallest cog size: %s" %(
                largest_cog, smallest_cog))
        self.cog_analysis = ""

        # save original cog names hitting the hard limit
        if len(valid_cogs) > self.cog_hard_limit:
            log.warning("Applying hard limit number of COGs: %d out of %d available" %(self.cog_hard_limit, len(valid_cogs)))
        self.raw_cogs = valid_cogs[:self.cog_hard_limit]
        self.cogs = []
        # Translate sequence names into the internal DB names
        sp_repr = defaultdict(int)
        sizes = []
        for co in self.raw_cogs:
            sizes.append(len(co))
            for sp, seq in co:
                sp_repr[sp] += 1
            co_names = ["%s%s%s" %(sp, GLOBALS["spname_delimiter"], seq) for sp, seq in co]
            encoded_names = db.translate_names(co_names)
            if len(encoded_names) != len(co):
                print set(co) - set(encoded_names.keys())
                raise DataError("Some sequence ids could not be translated")
            self.cogs.append(encoded_names.values())

        # ERROR! COGs selected are not the prioritary cogs sorted out before!!!
        # Sort Cogs according to the md5 hash of its content. Random
        # sorting but kept among runs
        #map(lambda x: x.sort(), self.cogs)
        #self.cogs.sort(lambda x,y: cmp(md5(','.join(x)), md5(','.join(y))))
        
        log.log(28, "Analysis of current COG selection:")
        for sp, ncogs in sorted(sp_repr.items(), key=lambda x:x[1], reverse=True):
            log.log(28, " % 30s species present in % 6d COGs (%0.1f%%)" %(sp, ncogs, 100 * ncogs/float(len(self.cogs))))
                
        log.log(28, " %d COGs selected with at least %d species out of %d" %(len(self.cogs), min_species, len(all_species)))
        log.log(28, " Average COG size %0.1f/%0.1f +- %0.1f" %(numpy.mean(sizes), numpy.median(sizes), numpy.std(sizes)))

        # Some consistency checks
        missing_sp = (all_species) - set(sp_repr.keys())
        if missing_sp:
            log.error("missing or not single-copy species under current cog selection: %s" %missing_sp)
            raise TaskError()

        CogSelectorTask.store_data(self, self.cogs, self.cog_analysis)

if __name__ == "__main__":
    ## TEST CODE
    import argparse
    parser = argparse.ArgumentParser()

    # Input data related flags
    
    parser.add_argument("--cogs_file", dest="cogs_file",
                        required=True,
                        help="Cogs file")

    parser.add_argument("--spname_delimiter", dest="spname_delimiter",
                             type=str, default = "_",
                             help="species name delimiter character")

    parser.add_argument("--target_sp", dest="target_sp",
                             type=str, nargs="+",
                             help="target species sperated by")

    parser.add_argument("-m", dest="missing_factor",
                             type=float, required=True,
                             help="missing factor for cog selection")

    parser.add_argument("--max_missing", dest="max_missing_factor",
                             type=float, default = 0.3,
                             help="max missing factor for cog selection")
    
    parser.add_argument("--total_species", dest="total_species",
                             type=int, required=True,
                             help="total number of species in the analysis")
    
    args = parser.parse_args()
    
    GLOBALS["cogs_file"] = args.cogs_file
    GLOBALS["spname_delimiter"] = args.spname_delimiter
    target_sp = args.target_sp
    logging.basicConfig(level=logging.DEBUG)
    log = logging
    GLOBALS["target_species"] = [1] * args.total_species

    conf = { "user": {"_species_missing_factor": args.missing_factor,
                      "_max_species_missing_factor": args.max_missing_factor,
                      "_max_cogs": 10000
                  }}
    CogSelectorTask.store_data=lambda a,b,c: True
    C =  CogSelector(set(target_sp), set(), "aa", conf, "user")

    db.translate_names = lambda x:  dict([(n,n) for n in x])
    
    C.finish()
