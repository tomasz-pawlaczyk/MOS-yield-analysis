import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

print("=== RUNNING ANALYSIS 4: CHRONOLOGICAL PROCESS-BASED QUALIFICATION SYSTEM ===")

os.makedirs("../figures", exist_ok=True)

try:
    df = pd.read_csv("../data/wafer_fab_data_raw.csv")
except FileNotFoundError:
    print("Error: '../data/wafer_fab_data_raw.csv' not found!")
    exit()

LIMITS = {
    'vth_lsl': 0.61,
    'vth_usl': 0.69,
    'res_usl': 1.45,
    'leakage_usl': 15.0,
    'particles_usl': 15,
    'alignment_usl': 20.0
}

# Chronological decision logic tracking the actual fab timeline
def qualify_wafer_chronological(row):
    # STEP 1: Oxidation (Irreversible gate oxide failures)
    if row['threshold_voltage_v'] < LIMITS['vth_lsl'] or row['threshold_voltage_v'] > LIMITS['vth_usl']:
        return 'REJECT'

    # STEP 2: Photolithography (Reversible alignment drift -> stripped and reworked)
    if row['lithography_alignment_nm'] > LIMITS['alignment_usl']:
        return 'REWORK'

    # STEP 3: Downstream Processes & E-Test (Irreversible backend defects)
    if (row['line_resistance_ohm'] > LIMITS['res_usl'] or
            row['leakage_current_na'] > LIMITS['leakage_usl'] or
            row['particle_count'] > LIMITS['particles_usl']):
        return 'REJECT'

    return 'PASS'

df['qualification_status'] = df.apply(qualify_wafer_chronological, axis=1)

total_wafers = len(df)
status_counts = df['qualification_status'].value_counts()

pass_count = status_counts.get('PASS', 0)
rework_count = status_counts.get('REWORK', 0)
reject_count = status_counts.get('REJECT', 0)

yield_pct = (pass_count / total_wafers) * 100
rework_pct = (rework_count / total_wafers) * 100
reject_pct = (reject_count / total_wafers) * 100

print("\n--- UPDATED YIELD ENGINEERING REPORT ---")
print(f"Total Fab Volume: {total_wafers} silicon wafers")
print(f" -> PASS (Final Yield):  {pass_count} pcs ({yield_pct:.1f}%)")
print(f" -> REWORK (Lithography): {rework_count} pcs ({rework_pct:.1f}%)")
print(f" -> REJECT (Scrap/Waste): {reject_count} pcs ({reject_pct:.1f}%)")

df.to_csv("../data/wafer_fab_data_qualified.csv", index=False)

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
labels = [f'PASS ({yield_pct:.1f}%)', f'REWORK ({rework_pct:.1f}%)', f'REJECT ({reject_pct:.1f}%)']
sizes = [pass_count, rework_count, reject_count]
colors = ['#2ecc71', '#f1c40f', '#e74c3c']

plt.figure(figsize=(7, 7))
plt.pie(
    sizes,
    labels=labels,
    colors=colors,
    startangle=50,
    pctdistance=0.85,
    textprops={'weight': 'bold', 'fontsize': 11}
)

centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)

plt.title('Global Fab Yield Structure\nBased on Chronological Process Flow Kpi', fontweight='bold', fontsize=13)
plt.tight_layout()
plt.savefig("../figures/08_yield_qualification_breakdown.png", dpi=300)
plt.close()

print("\n[Success] Plot 08 updated and formatted perfectly inside '../figures/'.")