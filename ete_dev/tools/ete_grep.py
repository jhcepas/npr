#!/usr/bin/env python
import os
import sys
from math import sqrt
from common import __CITATION__, argparse, Tree, print_table
    
__DESCRIPTION__ = '''
#  - treedist -
# ===================================================================================
#  
# ete_grep filter a list of trees using custom filters
#  
# %s
#  
# ===================================================================================
'''% __CITATION__


def main(argv):
    parser = argparse.ArgumentParser(description=__DESCRIPTION__, 
                            formatter_class=argparse.RawDescriptionHelpFormatter)
    
    args = parser.parse_args(argv)
    print 'Not available yet'
    
    print __DESCRIPTION__
                                     
if __name__ == '__main__':
    main(sys.argv[1:])

