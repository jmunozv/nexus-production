import sys, os
import subprocess



###
def get_host_name() -> str :

  local_host = os.uname()[1]
  my_host = "local"
  if    "majorana"  in local_host: my_host = "majorana"
  elif  "neutrinos" in local_host: my_host = "neutrinos"
  elif  "harvard"   in local_host: my_host = "harvard"

  return my_host



###
def get_exec_path() -> str :

  ## Getting local host
  host = get_host_name()

  if (host == "local"):     return "/Users/Javi/Development/nexus/bin/"
  if (host == "harvard"):   return "/n/holystore01/LABS/guenette_lab/Users/jmunozv/Development/nexus/bin/"
  if (host == "majorana"):  return "/home/jmunoz/Development/nexus/bin/"
  if (host == "neutrinos"): return "/Users/Javi/Development/nexus/bin/"



###
def give_tmp_harvard_path(fname : str) -> str :
  tmp_path = "/n/holyscratch01/guenette_lab/Users/jmunozv/"
  return tmp_path + fname.split("/")[-1]



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
                        dst_fname    : str,
                        log_fname    : str,
                        num_evts     : int
                       )            -> None :

  tmp_log_fname = give_tmp_harvard_path(log_fname)
  tmp_dst_fname = give_tmp_harvard_path(dst_fname)

  content  = "#!/bin/bash\n"

  content += "#SBATCH -n 1            # Number of cores requested\n"
  content += "#SBATCH -N 1            # Ensure that all cores are on one machine\n"
  content += "#SBATCH -t 2500         # Runtime in minutes\n"
  content += "#SBATCH -p guenette     # Partition to submit to\n"
  content += "#SBATCH --mem=1000      # Memory per cpu in MB (see also –mem-per-cpu)\n"
  content += "#SBATCH -o tmp/%j.out   # Standard out goes to this file\n"
  content += "#SBATCH -e tmp/%j.err   # Standard err goes to this filehostname\n"

  content += "source /n/home11/jmunozv/.bashrc\n"
  content += "source /n/home11/jmunozv/.setNEXUS\n"

  content += f"{exe_path}nexus -b {init_fname} -n {num_evts} > {tmp_log_fname}\n"

  content += f"mv {tmp_log_fname}    {log_fname}\n"
  content += f"mv {tmp_dst_fname}.h5 {dst_fname}.h5\n"

  script_file = open(script_fname, 'w')
  script_file.write(content)
  script_file.close()



###
def run_sim(exe_path   : str,
            init_fname : str,
            dst_fname  : str,
            log_fname  : str,
            num_evts   : int
           )          -> None :

  ## Getting local host
  host = get_host_name()

  ## Runing locally
  if host == "local":
    inst = [exe_path + "nexus", "-b", init_fname, "-n", str(num_evts)]
    my_env = os.environ.copy()
    subprocess.run(inst, env=my_env, stdout=open(log_fname, 'w'))


  ## Runing in HARVARD queue system
  elif host == "harvard":

    # Limit the maximum number of jobt to run at the same time
    while int(os.popen('squeue -u $USER | wc -l').read()) > 400:
      sleep(30)

    script_fname = "sim.slurm"
    #exe_path = "/n/holystore01/LABS/guenette_lab/Users/jmunozv/Development/nexus/bin/"
    make_harvard_script(script_fname, exe_path, init_fname, dst_fname, log_fname, num_evts)
    os.system(f"sbatch {script_fname}")
    

  ## Runing in MAJORANA queue system
  elif host == "majorana":
    script_fname = "sim.script"
    make_majorana_script(script_fname, exe_path, init_fname, log_fname, num_evts)
    os.system(f"qsub -N tst {script_fname}")
    

  # No other machine is supported yet
  else:
    print(f"Light Table simulations in {host} are not supported yet.")
    sys.exit()
