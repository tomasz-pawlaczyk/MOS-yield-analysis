import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

os.makedirs("../figures", exist_ok=True)

print("=== RUNNING ANALYSIS 2: CLEANROOM CLEANLINESS AND KILLER DEFECTS ===")

try:
    df = pd.read_csv("../data/wafer_fab_data_raw.csv")
except FileNotFoundError:
    print("Error: '../data/wafer_fab_data_raw.csv' not found!")
    exit()

# Statistical breakdown for particle contamination
lot_stats = df.groupby('lot_id')['particle_count'].agg(['mean', 'max', 'std']).reset_index()
CRITICAL_PARTICLE_LIMIT = 10.0
contaminated_lots = lot_stats[lot_stats['mean'] > CRITICAL_PARTICLE_LIMIT]

print("\n--- PARTICLES CONTROL REPORT (MES CONTAMINATION LOG) ---")
print(f"Global average particle count across fab: {df['particle_count'].mean():.2f}")
print("\nProduction lots violating ISO Cleanroom cleanliness standards:")
for _, row in contaminated_lots.iterrows():
    print(f" -> Lot: {row['lot_id']} | Average Particles: {row['mean']:.1f} | Max on Wafer: {row['max']}")

correlation = df['particle_count'].corr(df['leakage_current_na'])
print(f"\nPearson Correlation Coefficient (Particles vs Leakage Current): {correlation:.4f}")

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

plt.figure(figsize=(14, 6))
df_sorted = df.sort_values('lot_id')
sns.boxplot(data=df_sorted, x='lot_id', y='particle_count', color='#e74c3c', flierprops={"marker": "x"})
plt.axhline(y=CRITICAL_PARTICLE_LIMIT, color='black', linestyle='--', linewidth=2, label='Cleanliness Control Limit')
plt.title('Particle Contamination Distribution across Production Lots', fontweight='bold', fontsize=14)
plt.xlabel('Production Lot ID')
plt.ylabel('Particle Count per Wafer [pcs]')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig("../figures/04_cleanroom_lots_boxplot.png", dpi=300)
plt.close()

plt.figure(figsize=(9, 6))
df['defect_class'] = 'Normal'
df.loc[(df['particle_count'] > 20) & (df['leakage_current_na'] > 50), 'defect_class'] = 'Killer Defect (Breakdown)'
df.loc[(df['particle_count'] > 20) & (df['leakage_current_na'] <= 50), 'defect_class'] = 'Matrix-Inactive Contamination'

sns.scatterplot(
    data=df,
    x='particle_count',
    y='leakage_current_na',
    hue='defect_class',
    palette={'Normal': '#2ecc71', 'Matrix-Inactive Contamination': '#f1c40f', 'Killer Defect (Breakdown)': '#d35400'},
    alpha=0.7,
    edgecolor=None
)
plt.yscale('log')
plt.title('Correlation: Particle Contamination vs Dielectric Leakage Current', fontweight='bold')
plt.xlabel('Particle Count per Wafer [pcs]')
plt.ylabel('Leakage Current [nA] (Log Scale)')
plt.grid(True, which="both", linestyle='--', alpha=0.5)
plt.legend(title='Physical Structure Status')
plt.tight_layout()
plt.savefig("../figures/05_killer_defects_correlation.png", dpi=300)
plt.close()

print("\n[Success] Plots 04 and 05 saved to '../figures/'.")