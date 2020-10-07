import sys, os
import subprocess

from typing import List
from typing import Tuple
from typing import Dict


PATHS = {
  "local": {
    "exe_path" : "/Users/Javi/Development/nexus/",
    "base_path": "/Users/Javi/Development/nexus-production-test/"
  },

  "harvard": {
    "exe_path" : "/n/holystore01/LABS/guenette_lab/Users/jmunozv/Development/nexus/bin/",
    "base_path": "/n/holystore01/LABS/guenette_lab/Users/jmunozv/Development/FLEX100/201005/e-/"
  },

  "majorana": {
    "exe_path" : "/home/jmunoz/Development/nexus/bin/",
    "base_path": "/home/jmunoz/Development/nexus-production-test/"
  },

  "neutrinos": {
    "exe_path" : "/Users/Javi/Development/nexus/",
    "base_path": "/Users/Javi/Development/nexus-production-test/"
  }
}



###
def get_host_name() -> str :

  local_host = os.uname()[1]
  my_host = "local"
  if    "majorana"  in local_host: my_host = "majorana"
  elif  "neutrinos" in local_host: my_host = "neutrinos"
  elif  "harvard"   in local_host: my_host = "harvard"

  return my_host



###
def get_paths() -> Tuple[str, str, str, str] :

  ## Getting local host
  host = get_host_name()

  # Getting PATHS of current host
  exe_path  = PATHS[host]["exe_path"]
  base_path = PATHS[host]["base_path"]

  if not os.path.isdir(base_path): os.makedirs(base_path)

  # Making working PATHs
  config_path = base_path + 'config/'
  if not os.path.isdir(config_path): os.makedirs(config_path)

  log_path = base_path    + 'log/'
  if not os.path.isdir(log_path): os.makedirs(log_path)

  dst_path = base_path    + 'dst/'
  if not os.path.isdir(dst_path): os.makedirs(dst_path)

  return exe_path, config_path, log_path, dst_path



###
def make_majorana_script(script_fname : str,
                         exe_path     : str,
                         init_fname   : str,
                         log_fname    : str,
                         num_evts     : int
                        )            -> None :
    
  content  = "#PBS -q medium\n"
  content += "#PBS -M jmunoz@ific.uv.es\n"
  content += "#PBS -m ae\n"
  content += "#PBS -o ./tmp\n"
  content += "#PBS -e ./tmp\n"
  content += "#PBS -j oe\n"
  
  content += "source $HOME/.bashrc\n"
  content += "source $HOME/.setNEXUS2\n"

  content += f"{exe_path}nexus -b {init_fname} -n {num_evts} > {log_fname}\n"

  script_file = open(script_fname, 'w')
  script_file.write(content)
  script_file.close()



###
def make_harvard_script(script_fname : str,
                        exe_path     : str,
                        init_fname   : str,
                        log_fname    : str,
                        num_evts     : int
                       )            -> None :

  content  = "#!/bin/bash\n"

  content += "#SBATCH -n 1            # Number of cores requested\n"
  content += "#SBATCH -N 1            # Ensure that all cores are on one machine\n"
  content += "#SBATCH -t 2000         # Runtime in minutes\n"
  content += "#SBATCH -p guenette     # Partition to submit to\n"
  content += "#SBATCH --mem=1500      # Memory per cpu in MB (see also –mem-per-cpu)\n"
  content += "#SBATCH -o tmp/%j.out   # Standard out goes to this file\n"
  content += "#SBATCH -e tmp/%j.err   # Standard err goes to this filehostname\n"

  content += "source /n/home11/jmunozv/.bashrc\n"
  content += "source /n/home11/jmunozv/.setNEXUS\n"

  content += f"{exe_path}nexus -b {init_fname} -n {num_evts} > {log_fname}\n"

  script_file = open(script_fname, 'w')
  script_file.write(content)
  script_file.close()



###
def run_sim(exe_path   : str,
            init_fname : str,
            log_fname  : str,
            num_evts   : int
           )          -> None :

  ## Getting local host
  host = get_host_name()

  ## Runing locally
  if host == "local":
    inst = [exe_path + "nexus", "-b", init_fname, "-n",
            str(num_evts), ">", log_fname]
    #os.system("source /Users/Javi/.profile")
    #os.system("source /Users/Javi/.setNEXUS")
    my_env = os.environ.copy()
    subprocess.run(inst, env=my_env)
        

  ## Runing in MAJORANA queue system
  elif host == "majorana":
    script_fname = "sim.script"
    make_majorana_script(script_fname, exe_path, init_fname, log_fname, num_evts)
    os.system(f"qsub -N tst {script_fname}")
    

  ## Runing in HARVARD queue system
  elif host == "harvard":
    script_fname = "sim.slurm"
    exe_path = "/n/holystore01/LABS/guenette_lab/Users/jmunozv/Development/nexus/bin/"
    make_harvard_script(script_fname, exe_path, init_fname, log_fname, num_evts)
    os.system(f"sbatch {script_fname}")
    

  # No other machine is supported yet
  else:
    print(f"Light Table simulations in {host} are not supported yet.")
    sys.exit()
