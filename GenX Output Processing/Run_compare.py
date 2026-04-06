#!/bin/sh
#SBATCH -N 1             # Request 1 node
#SBATCH -n 1             # Request 1 task
#SBATCH -c 1             # Request 1 core per task
#SBATCH --mem=1G         # Request GB of memory
#SBATCH -t 0:01:00       # Request 1 minutes of time
#SBATCH -o output.log    # Redirect standard output to output.log
#SBATCH -e error.log     # Redirect standard error to error.log
#SBATCH --mail-type=end                    # notifications for job done & fail
#SBATCH --mail-user=clarabloom@princeton.edu  # send-to address

module load anaconda3/2025.6

# Run Python script

python compare_cases.py > case_diff.txt
