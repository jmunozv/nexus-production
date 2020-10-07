#!/usr/bin/env python

import os
import sys
import pandas   as pd
from   glob import glob

try:
    path = sys.argv[1]
    print(f"\nAnalyzing {path}")    
except IndexError:
    print("\nUsage:   check_output.py <path_name>\n")
    sys.exit()

ifnames = glob(path + '/*.h5')
ifnames.sort()

tot_files = len(ifnames)
print(f"Total files in PATH: {tot_files} \n")    


corrupted_files = 0 
for ifname in ifnames:

    try :
        #sns_response = pd.read_hdf(ifname, "/MC/sns_response")
        sns_positions = pd.read_hdf(ifname, "/MC/sns_positions")
        print(f"{ifname} OK.")

    except:
        corrupted_files += 1
        print(f"{ifname} corrupted. Removing ...")
        os.remove(ifname)

print(f"\nSummary: {corrupted_files} corrupted files out of {tot_files}\n")