import pandas as pd
import matplotlib.pyplot as plt
import os

BASE_PATH = "/Users/clarabloom/Thesis/Final_Model_Results/BASE"
FIG_PATH = os.path.join(BASE_PATH, "figures")

# ***********************
# PLOT System EMISSIONS
# ***********************

years = [2030, 2035, 2045]

emis = pd.read_csv("/Users/clarabloom/Thesis/Final_Model_Results/BASE/Load_and_Emissions.csv")

plt.figure(figsize=(14, 6))

for case in emis["CaseName"].unique():
    subset = emis[emis["CaseName"] == case]
    
    plt.plot(years,
             [subset["Total_System_Emissions_p1"].values[0],
              subset["Total_System_Emissions_p2"].values[0],
              subset["Total_System_Emissions_p3"].values[0]],
             marker="o",
             label=case)

plt.xlabel("Planning Period")
plt.ylabel("Total System Emissions (tons)")
plt.title("System Emissions by Case")
plt.xticks([2030,2035,2045])
plt.legend(bbox_to_anchor=(1.05, 1), loc="best", fontsize=9, borderaxespad=0)
plt.grid(True)

# save figure to base > figures folder
plt.savefig("/Users/clarabloom/Thesis/Final_Model_Results/BASE/figures/System_Emis_by_Case_and_Period.png", dpi=300, bbox_inches="tight")
plt.show()

# ***********************
# PLOT NJ EMISSIONS
# ***********************
plt.figure()

for case in emis["CaseName"].unique():
    subset = emis[emis["CaseName"] == case]
    
    plt.plot(years,
             [subset["Total_NJ_Emissions_p1"].values[0],
              subset["Total_NJ_Emissions_p2"].values[0],
              subset["Total_NJ_Emissions_p3"].values[0]],
             marker="o",
             label=case)

plt.xlabel("Planning Period")
plt.ylabel("NJ Emissions (tons)")
plt.title("NJ Emissions by Case")
plt.xticks([2030,2035,2045])
plt.legend()
plt.grid(True)

# save figure to base > figures folder
plt.savefig("/Users/clarabloom/Thesis/Final_Model_Results/BASE/figures/NJ_Emis_by_Case_and_Period.png", dpi=300)
plt.show()

