from pathlib import Path

# ==================================================
# PATH
# ==================================================

LDS_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lds")

EXCLUDE_CASE = "lds_cesincccstechinstate"

# ==================================================
# UPDATE FUNCTION
# ==================================================

def update_run_sh(run_path):
    with open(run_path, "r") as f:
        lines = f.readlines()

    new_lines = []

    for line in lines:
        if line.startswith("#SBATCH --time="):
            new_lines.append("#SBATCH --time=15:00:00\n")
        elif line.startswith("#SBATCH --mem-per-cpu="):
            new_lines.append("#SBATCH --mem-per-cpu=9G\n")
        else:
            new_lines.append(line)

    with open(run_path, "w") as f:
        f.writelines(new_lines)

    print(f"Updated: {run_path}")


# ==================================================
# MAIN
# ==================================================

def main():
    for case in LDS_DIR.iterdir():
        if not case.is_dir():
            continue

        case_name = case.name

        if case_name == EXCLUDE_CASE:
            print(f"Skipping {case_name}")
            continue

        run_file = case / "Run.sh"

        if run_file.exists():
            update_run_sh(run_file)
        else:
            print(f"⚠ Missing Run.sh in {case_name}")

    print("\nDone!")

if __name__ == "__main__":
    main()