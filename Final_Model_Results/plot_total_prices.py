import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("/Users/clarabloom/Thesis/Final_Model_Results/BASE/Prices_by_Zone_by_Year_ALL_CASES (1).csv")

years = [2030, 2035, 2045]

line_styles = ['-',  ':',  '-.',  '--', '-',  ':',  '-.',  '--',  ':',  '-.']
markers     = ['o',  's',  '^',  'o',  's',  '^',  'o',  's',  '^',  'o' ]
colors = [
    '#48ABE8', '#F29D13', '#77B053', '#F5867F', '#9368B3',
    '#9E5139', '#F291C7', '#393E41', '#B7C480', '#7CC5CC'
]

fig, ax = plt.subplots(figsize=(10, 6))

for i, (_, row) in enumerate(df.iterrows()):
    prices = [row['Total_Price_p1'], row['Total_Price_p2'], row['Total_Price_p3']]
    ax.plot(years, prices,
            linestyle=line_styles[i],
            marker=markers[i],
            color=colors[i],
            label=row['CaseName'],
            linewidth=2,
            markersize=8)

ax.set_xticks(years)
ax.set_xlabel('Year')
ax.set_ylabel('Total NJ Energy Price ($/MWh)')
ax.set_title('Total NJ Energy Price Over Time by Case')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
ax.grid(linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('/Users/clarabloom/Thesis/Final_Model_Results/BASE/FIGURES/NJ_Prices.png', dpi=150)
plt.show()
print("Plot saved.")