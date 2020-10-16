import sys

from datetime import datetime


STORE_OPT_PARTICLES = False


###
def get_seed() -> int :
  dt = datetime.now()
  return dt.microsecond



##### INIT FUNCTIONS ##########################################

###
def init_geometry_str(det_name : str) -> str :

  if   ("NEXT100" == det_name): det_name += "_OPT"         # XXX To be deleted asap
  elif ("FLEX"    in det_name): det_name  = "NEXT_FLEX"

  return f"/Geometry/RegisterGeometry {det_name}\n"



###
def init_generator_str(evt_type : str) -> str :
  if (evt_type == "Xe136_bb0nu") or (evt_type == "Xe136_bb2nu"):
    content = "/Generator/RegisterGenerator DECAY0\n"

  elif (evt_type == "Bi214") or (evt_type == "Tl208"):
    content = "/Generator/RegisterGenerator ION_GUN\n"

  elif evt_type == "Kr83":
    content = "/Generator/RegisterGenerator Kr83m\n"

  elif evt_type == "Scintillation":
    content = "/Generator/RegisterGenerator SCINTGENERATOR\n"

  elif evt_type == "e-":
    content = "/Generator/RegisterGenerator SINGLE_PARTICLE\n"

  else:
    print(f"ERROR: No Init-Generator-String defined for {evt_type}.")
    sys.exit()

  return content



###
def init_actions_str(evt_type : str) -> str :

  # Run action
  content  = "/Actions/RegisterRunAction      DEFAULT\n"

  # Event action
  if ((evt_type == "Xe136_bb0nu") or (evt_type == "Xe136_bb2nu") or
      (evt_type == "Bi214")       or (evt_type == "Tl208")       or
      (evt_type == "Kr83")        or (evt_type == "e-")):
    content += "/Actions/RegisterEventAction    DEFAULT\n"
  elif (evt_type == "Scintillation"):
    content += "/Actions/RegisterEventAction    SAVE_ALL\n"
  else:
    print (f"No EventAction defined for evt_type: {evt_type}")
    exit(1)

  # Tracking Action
  if STORE_OPT_PARTICLES:
    content += "/Actions/RegisterTrackingAction OPTICAL\n"
  else:
    content += "/Actions/RegisterTrackingAction DEFAULT\n"

  # Stepping Action
  content += "/Actions/RegisterSteppingAction ANALYSIS\n"

  return content



###
def init_physics_str(sim_mode : str) -> str :
  content  = "/PhysicsList/RegisterPhysics G4EmStandardPhysics_option4\n"
  content += "/PhysicsList/RegisterPhysics G4DecayPhysics\n"
  content += "/PhysicsList/RegisterPhysics G4RadioactiveDecayPhysics\n"
  content += "/PhysicsList/RegisterPhysics NexusPhysics\n"
  content += "/PhysicsList/RegisterPhysics G4StepLimiterPhysics\n"

  if (sim_mode == "full"):
    content += "/PhysicsList/RegisterPhysics G4OpticalPhysics\n"

  return content



###
def init_extra_str(exe_path     : str,
                   config_fname : str,
                   evt_type     : str) -> str :
  content  = f"/nexus/RegisterMacro {config_fname}\n"

  if (evt_type == "Bi214"):
    content += "/nexus/RegisterDelayedMacro {exe_path}macros/physics/Bi214.mac\n"

  return content



###
def make_init_file(det_name     : str,
                   exe_path     : str,
                   init_fname   : str,
                   config_fname : str,
                   evt_type     : str,
                   sim_mode     : str
                  )            -> None :

  content = f'''### GEOMETRY
{init_geometry_str(det_name)}
### GENERATOR
{init_generator_str(evt_type)}
### ACTIONS
{init_actions_str(evt_type)}
### PHYSICS
{init_physics_str(sim_mode)}
### EXTRA CONFIGURATION
{init_extra_str(exe_path, config_fname, sim_mode)}
'''
  init_file = open(init_fname, 'w')
  init_file.write(content)
  init_file.close()




##### CONFIG FUNCTIONS ##########################################

###
def config_geometry_str(det_name : str) -> str :
  
  # Geometry Content
  template_file = f"templates/{det_name}.geometry.config"
  geometry_content = open(template_file).read()

  return geometry_content  
    



###
def config_generator_str(det_name   : str,
                         evt_type   : str,
                         evt_source : str) -> str :

  content = ""

  if   (det_name == "NEXT_NEW"): det_name_str = "NextNew"
  elif (det_name == "NEXT100"):  det_name_str = "Next100"
  elif ("FLEX" in det_name):     det_name_str = "NextFlex"

  evt_source_str = evt_source

  if "(" in evt_source:
    evt_source_str = "AD_HOC"
    tmp = evt_source[1:-1].split(',')
    content += f"/Geometry/{det_name_str}/specific_vertex_X  {tmp[0]} mm\n"
    content += f"/Geometry/{det_name_str}/specific_vertex_Y  {tmp[1]} mm\n"
    content += f"/Geometry/{det_name_str}/specific_vertex_Z  {tmp[2]} mm\n"

  # BB decays
  if (evt_type == "Xe136_bb0nu") or (evt_type == "Xe136_bb2nu"):  

    dec_mode = 1
    if (evt_type == "Xe136_bb2nu"): dec_mode = 4

    content += f"/Generator/Decay0Interface/Xe136DecayMode {dec_mode}\n"
    content += "/Generator/Decay0Interface/inputFile none\n"
    content += "/Generator/Decay0Interface/EnergyThreshold 2.3 MeV\n"
    content += "/Generator/Decay0Interface/Ba136FinalState 0.\n"
    content += f"/Generator/Decay0Interface/region {evt_source_str}\n"

  # Backgrounds
  elif (evt_type == "Tl208") or (evt_type == "Bi214"):

    if   (evt_type == "Tl208"): Z, A = 81, 208
    elif (evt_type == "Bi214"): Z, A = 83, 214

    content += f"/Generator/IonGun/atomic_number {Z}\n"
    content += f"/Generator/IonGun/mass_number {A}\n"
    content += f"/Generator/IonGun/region {evt_source_str}\n"

  # Kr83
  elif evt_type == "Kr83":
    content += f"/Generator/Kr83mGenerator/region {evt_source_str}\n"

  # Scintillation
  elif evt_type == "Scintillation":
    content += f"/Generator/ScintGenerator/region   {evt_source_str}\n"
    content += "/Generator/ScintGenerator/nphotons 10000\n"

  # Single e-
  elif evt_type == "e-":
    content += f"/Generator/SingleParticle/region   {evt_source_str}\n"
    content += "/Generator/SingleParticle/particle e-\n"
    content += "/Generator/SingleParticle/min_energy  2.458 MeV\n"
    content += "/Generator/SingleParticle/max_energy  2.458 MeV\n"

  return content



###
def config_actions_str(evt_type : str) -> str :
  content = ""
  return content



###
def config_physics_str(sim_mode : str) -> str :
  content = ""

  if sim_mode == "fast":
    opt_procs = False
    content  += f"/PhysicsList/Nexus/clustering          {opt_procs}\n"
    content  += f"/PhysicsList/Nexus/drift               {opt_procs}\n"
    content  += f"/PhysicsList/Nexus/electroluminescence {opt_procs}\n"

  else:
    opt_procs = True
    content  += f"/process/optical/scintillation/setTrackSecondariesFirst {opt_procs}\n"
    content  += f"/PhysicsList/Nexus/clustering          {opt_procs}\n"
    content  += f"/PhysicsList/Nexus/drift               {opt_procs}\n"
    content  += f"/PhysicsList/Nexus/electroluminescence {opt_procs}\n"

  return content



###
def make_config_file(det_name      : str,
                     config_fname  : str,
                     dst_fname     : str,
                     evt_type      : str,
                     evt_source    : str,
                     sim_mode      : str,
                     first_evt_idx : int
                    )             -> None :

  content = f'''### GEOMETRY
{config_geometry_str(det_name)}
### GENERATOR
{config_generator_str(det_name, evt_type, evt_source)}
### ACTIONS
{config_actions_str(evt_type)}
### PHYSICS
{config_physics_str(sim_mode)}
### VERBOSITIES
/control/verbose   0
/run/verbose       0
/event/verbose     0
/tracking/verbose  0

### CONTROL
/nexus/random_seed            {get_seed()}
/nexus/persistency/start_id   {first_evt_idx}
/nexus/persistency/outputFile {dst_fname}
'''
  #print(content)
  config_file = open(config_fname, 'w')
  config_file.write(content)
  config_file.close()
