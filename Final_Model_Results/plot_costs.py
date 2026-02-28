import pandas as pd
import matplotlib.pyplot as plt
import os

BASE_PATH = "/Users/clarabloom/Thesis/Final_Model_Results/BASE"
FIG_PATH = os.path.join(BASE_PATH, "figures")

# ***********************
# PLOT NJ COSTS
# ***********************

df = pd.read_csv(os.path.join(BASE_PATH, "Costs_by_Case_and_Period_ALL_CASES.csv"))

df_long = df.melt(
    id_vars="CaseName",
    value_vars=["NJ_Cost_p1", "NJ_Cost_p2", "NJ_Cost_p3"],
    var_name="Period",
    value_name="Cost"
)

df_long["Period"] = df_long["Period"].str.extract(r"p(\d)").astype(int)
df_long["Cost_Billions"] = df_long["Cost"] / 1e9

plt.figure(figsize=(8,5))

for case in df_long["CaseName"].unique():
    subset = df_long[df_long["CaseName"] == case]
    plt.plot(subset["Period"], subset["Cost_Billions"], marker="o", label=case)

plt.xlabel("Planning Period")
plt.ylabel("NJ Cost (Billion $)")
plt.title("NJ Cost by Case and Planning Period")
plt.xticks([1,2,3])
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(os.path.join(FIG_PATH, "NJ_Cost_by_Case_and_Period.png"), dpi=300)
plt.show()
