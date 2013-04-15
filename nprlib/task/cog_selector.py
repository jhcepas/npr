import numpy
from StringIO import StringIO
import cPickle
from string import strip
from collections import defaultdict
import logging
import os
import time
log = logging.getLogger("main")


from nprlib.master_task import CogSelectorTask
from nprlib.errors import DataError
from nprlib.utils import (GLOBALS, print_as_table, generate_node_ids,
                          encode_seqname, md5, pjoin)
from nprlib import db

__all__ = ["MCLCogSelector"]

quote = lambda _x: '"%s"' %_x

class MCLCogSelector(CogSelectorTask):
    def __init__(self, target_sp, out_sp, seqtype, conf, confname):

        self.seed = conf[confname]["_seed"]
        self.missing_factor = float(conf[confname]["_species_missing_factor"])
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
        all_species = self.targets | self.outgroups
        min_species = len(all_species) - round(self.missing_factor * len(all_species))

        valid_cogs = []
        for cog in open(GLOBALS["cogs_file"]):
            sp2seqs = defaultdict(list)
            for sp, seqid in [map(strip, seq.split("_")) for seq in cog.split("\t")]:
                sp2seqs[sp].append(seqid)
            one2one_cog = set()
            for sp, seqs in sp2seqs.iteritems():
                if sp in all_species and len(seqs) == 1:
                    one2one_cog.add("%s_%s" %(sp, seqs[0]))
            if len(one2one_cog) >= min_species:
                valid_cogs.append(one2one_cog)
        
        self.raw_cogs = valid_cogs
        self.cog_analysis = ""
        self.cogs = []
        for co in self.raw_cogs:
            # self.cogs.append(map(encode_seqname, co))
            encoded_names = db.translate_names(co)
            if len(encoded_names) != len(co):
                print set(co) - set(encoded_names.keys())
                raise DataError("Some sequence ids could not be translated")
            self.cogs.append(encoded_names.values())

        # Sort Cogs according to the md5 hash of its content. Random
        # sorting but kept among runs
        map(lambda x: x.sort(), self.cogs)
        self.cogs.sort(lambda x,y: cmp(md5(','.join(x)), md5(','.join(y))))
        log.log(28, "%s COGs detected" %len(self.cogs))                
        tm_end = time.ctime()
        #open(pjoin(self.taskdir, "__time__"), "w").write(
        #    '\n'.join([tm_start, tm_end]))
        CogSelectorTask.store_data(self, self.cogs, self.cog_analysis)
