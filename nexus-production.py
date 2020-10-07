#!/usr/bin/env python

import sys, os

from host_utils import get_host_name
from host_utils import run_sim
from host_utils import get_paths

from sim_utils  import make_init_file
from sim_utils  import make_config_file


VERBOSITY = True

VALID_DETECTORS = ["NEXT_NEW", "NEXT100", "NEXT_FLEX"]

VALID_TYPES = ["Xe136_bb0nu", "Xe136_bb2nu", "Bi214", "Tl208",
               "Kr83", "Scintillation", "e-"]

# (Type scintillation corresponds to 1e4 photons)

VALID_MODES = ["fast", "full"]



########################################
############ DATA TO ANALYZE ###########

# sim: [evt_type, evt_src, total_events, events_dst, sim_mode]

#SIMS = [
#  ["Xe136_bb0nu",    "ACTIVE",        1e5,  1e4,  "fast"],
#  ["Bi214",          "FIELD_CAGE",    1e8,  1e7,  "fast"],
#  ["Tl208",          "READOUT_PLANE", 1e8,  1e7,  "fast"],
#  ["Kr83",           "ACTIVE",        5e4,  1e3,  "full"],
#  ["Scintillation",  "(0,0,20)",      1e8,  1e7,  "full"]
#]

DET_NAME = "NEXT_FLEX"

INITIAL_DST_INDEX = 0

SIMS = [
  ["e-",  "ACTIVE",  10000,  1000,  "fast"]
]

## Checking all options are VALID
assert DET_NAME in VALID_DETECTORS, f"{DET_NAME} is NOT a valid detector."

for sim in SIMS:
  evt_type, _, _, _, sim_mode = sim
  assert evt_type in VALID_TYPES, f"{evt_type} is NOT a valid event type."
  assert sim_mode in VALID_MODES, f"{sim_mode} is NOT a valid sim mode."



#######################################
############ RUN SIMULATION ###########

host = get_host_name()

exe_path, config_path, log_path, dst_path = get_paths()

if VERBOSITY:
  print(f"\n### RUNNING ON {host} HOST")
  print(f"# exe  PATH: {exe_path}")
  print(f"# conf PATH: {config_path}")
  print(f"# log  PATH: {log_path}")
  print(f"# dst  PATH: {dst_path}")


for sim in SIMS:
  evt_type, evt_src, total_events, events_dst, sim_mode = sim

  num_dsts = int(total_events / events_dst)

  if (total_events < events_dst):
    print(f"\n* WARNING {evt_type} - {evt_src} : Total Events  <  Events/File")
    num_dsts   = 1
    events_dst = total_events

  for i in range(num_dsts):
    dst_index       = INITIAL_DST_INDEX + i
    first_evt_index = dst_index * events_dst

    # Verbosing
    print("\n******************************************************************")
    print(f"***  {DET_NAME} - {evt_type} - {evt_src}   DST idx: {dst_index}   Num evts: {events_dst:.1e}  ***")

    evt_src_str = evt_src
    if "(" in evt_src:
      evt_src_str = evt_src[1:-1].replace(',', '_')

    # File names
    base_fname   = f"{DET_NAME}.{evt_type}.{evt_src_str}.{dst_index}"
    init_fname   = config_path + base_fname + '.init'
    config_fname = config_path + base_fname + '.config'
    log_fname    = log_path    + base_fname + '.log'
    dst_fname    = dst_path    + base_fname + '.next'
    
    if VERBOSITY: 
      print(f"* Init file:   {init_fname}")
      print(f"* Config file: {config_fname}")
      print(f"* Log file:    {log_fname}")
      print(f"* Dst file:    {dst_fname}.h5")

    # Making configuration files
    make_init_file  (DET_NAME, exe_path, init_fname, config_fname,
                     evt_type, sim_mode)

    make_config_file(DET_NAME, config_fname, dst_fname, evt_type,
                     evt_src, sim_mode, first_evt_index)

    # Running the simulation
    run_sim(exe_path, init_fname, log_fname, events_dst)
