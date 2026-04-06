#!/bin/sh
#SBATCH -N 1             # Request 1 node
#SBATCH -n 1             # Request 1 task
#SBATCH -c 1             # Request 1 core per task
#SBATCH --mem=1G         # Request GB of memory
#SBATCH -t 0:02:00       # Request 2 minutes of time
#SBATCH -o output.log    # Redirect standard output to output.log
#SBATCH -e error.log     # Redirect standard error to error.log
#SBATCH --mail-type=end                    # notifications for job done & fail
#SBATCH --mail-user=clarabloom@princeton.edu  # send-to address

module load anaconda3/2025.6

#Run Python script

#python compare_cases.py > case_diff.txt

#python fix_ng_coal.py


#python Calculate_Capacity.py
#python Calculate_Emissions.py
#python Calculate_Prices.py

#python update_lowng_files.py
#python update_highng_files.py

#python update_incccs.py

#python copy_file_info.py

#python Calculate_Generation.py
#python Calculate_Costs.py

#python Calculate_Cap_Emis_Price.py

#python update_highestamb.py

#python clean_cases.py
#python clean_results.py

#***************************
#python Process_All_Case_Outputs.py
#***************************

#python fix_esr.py

#python update_ambition_esr.py

#python new_policy.py

#python update_nuclear.py

#python move_cases.py

#python create_lds_future.py

#python create_battery_futures.py

#python update_Run_sh.py

#python check_ng.py

#python fix_ng.py

#python create_hightx.py

python calc_curtailment.py

python calc_nse.py

#python update_lds.py