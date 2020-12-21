#!/usr/bin/env python

import sys, os, json

from host_utils import run_sim
from host_utils import get_exec_path

from sim_utils  import make_init_file
from sim_utils  import make_config_file


#################### GENERALITIES ####################

VALID_DETECTORS = ["NEXT_NEW",                  # NEXT_NEW detector
                   "NEXT_NEW_PE",               # NEXT_NEW with PhotoElectric effect
                   "FLEX_NEW",                  # FLEX with NEW dimensions (ANODE: grid instead of plate)
                   "NEXT_FLEX",                 #
                   "NEXT100",                   # NEXT100 detector (initial config)
                   "FLEX100",                   # FLEX with NEXT100 initial config (To be checked)
                   "FLEX100_7_5",               # (To be checked)
                   "FLEX100_M10",               # (To be checked)
                   "FLEX100_M12",               # (To be checked)
                   "FLEX100_D3_M2_O6",          # Dist: 3mm   MaskThickn: 2mm  MaskHoleDiam: 6mm  Pitch: 15.3mm
                   "FLEX100_M2_O6",             # Dist: 15mm  MaskThickn: 2mm  MaskHoleDiam: 6mm  Pitch: 15.3mm
                   "FLEX100_M4_O6",             # Dist: 15mm  MaskThickn: 4mm  MaskHoleDiam: 6mm  Pitch: 15.3mm
                   "FLEX100_M6_O6",             # Dist: 15mm  MaskThickn: 6mm  MaskHoleDiam: 6mm  Pitch: 15.3mm
                   "FLEX100_M8_O6",             # Dist: 15mm  MaskThickn: 8mm  MaskHoleDiam: 6mm  Pitch: 15.3mm
                   "FLEX100_M6_O4",             # Dist: 15mm  MaskThickn: 6mm  MaskHoleDiam: 4mm  Pitch: 15.3mm
                   "FLEX100_M6_O8",             # Dist: 15mm  MaskThickn: 6mm  MaskHoleDiam: 8mm  Pitch: 15.3mm
                   "FLEX100_D3_M2_O6_P10",      # Dist: 3mm   MaskThickn: 2mm  MaskHoleDiam: 6mm  Pitch: 10.0mm
                   "FLEX100_M6_O6_P10",         # Dist: 15mm  MaskThickn: 6mm  MaskHoleDiam: 6mm  Pitch: 10.0mm
                   "FLEX100F_M6_O6",            # FLEX100_M6_O6 + fibers (No PMTs)
                   "FLEX100F_M6_O6_CathTeflon", # FLEX100_M6_O6 + fibers (No PMTs) + Teflon in CATHODE
                   "DEMOpp-Run5",               # DEMOpp-Run5 detector
                   "DEMOpp-Run7"                # DEMOpp-Run7 detector
                  ]

VALID_EVT_TYPES = ["Xe136_bb0nu",   
                   "Xe136_bb2nu",
                   "Bi214",
                   "Tl208",
                   "Kr83",
                   "Scintillation", # (1e4 photons)
                   "e-",            # Default energy: 2458 keV (Xe136 Qbb) 
                   "e+e-"           # Total     Ekin: 1592 keV (= Tl double scape peak)
                  ]


VALID_SIM_MODES = ["fast",  # Fast simulation (no optical photons)
                   "full"   # Full simulation
                  ]



#################### SETTINGS #########################

# Loading config file
try:
    config_fname = sys.argv[1]
except IndexError:
    print("\nUsage: python nexus-production.py config_file.json\n")
    sys.exit()

with open(config_fname) as config_file:
    config_data = json.load(config_file)

det_name    = config_data["det_name"]
evt_type    = config_data["evt_type"]
evt_src     = config_data["evt_src"]
sim_mode    = config_data["sim_mode"]
total_evts  = int(config_data["total_evts"])
evts_dst    = int(config_data["evts_dst"])
ini_dst_id  = int(config_data["ini_dst_id"])
output_path = config_data["output_path"]
verbosity   = config_data["verbosity"]

# Asserting input data is valid
assert det_name in VALID_DETECTORS, "Wrong Detector"
assert evt_type in VALID_EVT_TYPES, "Wrong Event Type"
assert sim_mode in VALID_SIM_MODES, "Wrong Simulation Mode"

# Number of dsts
num_dsts = int(total_evts / evts_dst)
if (total_evts < evts_dst):
    print("\n* WARNING: total events  <  events/dst")
    num_dsts   = 1
    events_dst = total_evts

# Working PATHs
config_path = output_path + '/config/'
log_path    = output_path + '/log/'
dst_path    = output_path + '/dst/'

if not os.path.isdir(output_path): os.makedirs(output_path)
if not os.path.isdir(config_path): os.makedirs(config_path)
if not os.path.isdir(log_path):    os.makedirs(log_path)
if not os.path.isdir(dst_path):    os.makedirs(dst_path)

# Executable path
exec_path = get_exec_path()

# Verbosing
if verbosity:
  print()
  print(f"Detector name   : {det_name}")
  print(f"Event type      : {evt_type}")
  print(f"Event source    : {evt_src}")
  print(f"Simulation mode : {sim_mode}")
  print(f"Total events    : {total_evts}")
  print(f"Events per dst  : {evts_dst}")
  print(f"Number of dsts  : {num_dsts}")
  print(f"Initial dst id  : {ini_dst_id}")
  print(f"Output PATH     : {output_path}")
  print(f"Executable PATH : {exec_path}")



#################### RUN SIMULATIONS ##################

for idx in range(num_dsts):

    # dst & event ids
    dst_id       = ini_dst_id + idx
    first_evt_id = dst_id * evts_dst

    # File names
    evt_src_str = evt_src
    # (Acomodating AD_HOC vertex to string)
    if "(" in evt_src:
        evt_src_str = evt_src[1:-1].replace(',', '_')

    base_fname   = f"{det_name}.{evt_type}.{evt_src_str}.{dst_id}"
    init_fname   = config_path + base_fname + '.init'
    config_fname = config_path + base_fname + '.config'
    log_fname    = log_path    + base_fname + '.log'
    dst_fname    = dst_path    + base_fname + '.next'

    # Making configuration files
    make_init_file  (det_name, exec_path, init_fname, config_fname,
                     evt_type, sim_mode)

    make_config_file(det_name, config_fname, dst_fname, evt_type,
                     evt_src, sim_mode, first_evt_id)

    # Verbosing
    if verbosity:
        print()
        print(f"* Simulating {evt_type} from {evt_src}   dst id: {dst_id} ({evts_dst:.1e} evts)")
        print(f"  Init file:   {init_fname}")
        print(f"  Config file: {config_fname}")
        print(f"  Log file:    {log_fname}")
        print(f"  Dst file:    {dst_fname}.h5")

    # Running the simulation
    run_sim(exec_path, init_fname, dst_fname, log_fname, evts_dst)
