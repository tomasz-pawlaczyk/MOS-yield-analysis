import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

print("=== RUNNING ANALYSIS 3: STATISTISTICAL PROCESS CONTROL (SPC) & OUTLIERS ===")

try:
    df = pd.read_csv("../data/wafer_fab_data_raw.csv")
except FileNotFoundError:
    print("Error: '../data/wafer_fab_data_raw.csv' not found!")
    exit()

df['wafer_num'] = df['wafer_id'].str.extract(r'(\d+)').astype(int)

print("\n--- SPC STATISTICAL ANALYSIS (3-SIGMA REJECTION RULE & IQR) ---")

# Method A: 3-Sigma Rule for Line Resistance
res_mean = df['line_resistance_ohm'].mean()
res_std = df['line_resistance_ohm'].std()
ucl_res = res_mean + 3 * res_std

outliers_res = df[df['line_resistance_ohm'] > ucl_res]
print(f"\n[3-Sigma Method] Line Resistance (UCL Limit: {ucl_res:.3f} Ohm):")
for _, row in outliers_res.iterrows():
    print(f" -> CRITICAL OUTLIER DETECTED: Wafer {row['wafer_id']} | Resistance: {row['line_resistance_ohm']} Ohm (Severe track damage!)")

# Method B: IQR (Interquartile Range) for CVD Layer Thickness
q1 = df['cvd_thickness_nm'].quantile(0.25)
q3 = df['cvd_thickness_nm'].quantile(0.75)
iqr = q3 - q1
lower_bound_cvd = q1 - 1.5 * iqr
upper_bound_cvd = q3 + 1.5 * iqr

outliers_cvd = df[(df['cvd_thickness_nm'] < lower_bound_cvd) | (df['cvd_thickness_nm'] > upper_bound_cvd)]
print(f"\n[IQR Method] CVD Thickness (Limits: {lower_bound_cvd:.1f} - {upper_bound_cvd:.1f} nm):")
for _, row in outliers_cvd.iterrows():
    status = "Under-deposition" if row['cvd_thickness_nm'] < lower_bound_cvd else "Over-deposition"
    print(f" -> CVD CHAMBER ANOMALY DETECTED ({status}): Wafer {row['wafer_id']} | Thickness: {row['cvd_thickness_nm']} nm")

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

plt.figure(figsize=(12, 5))
plt.plot(df['wafer_num'], df['line_resistance_ohm'], color='#7f8c8d', alpha=0.6, label='Wafer Measurements')
plt.scatter(outliers_res['wafer_num'], outliers_res['line_resistance_ohm'], color='#c0392b', marker='o', s=80, zorder=5, label='Critical Outlier (3-Sigma)')

plt.axhline(y=res_mean, color='green', linestyle='-', linewidth=1.5, label=f'Process Mean ({res_mean:.2f} Ohm)')
plt.axhline(y=ucl_res, color='red', linestyle='--', linewidth=2, label=f'Upper Control Limit UCL ({ucl_res:.2f} Ohm)')

plt.title('Line Resistance Control Chart (SPC Control Chart)', fontweight='bold')
plt.xlabel('Wafer Reference Number (Wafer ID)')
plt.ylabel('Line Resistance [Ohm]')
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig("../figures/06_spc_resistance_control_chart.png", dpi=300)
plt.close()

plt.figure(figsize=(9, 5))
sns.histplot(data=df, x='cvd_thickness_nm', bins=50, color='#34495e', kde=True, alpha=0.7)
for _, row in outliers_cvd.iterrows():
    plt.axvline(x=row['cvd_thickness_nm'], color='#e67e22', linestyle=':', linewidth=2)
    plt.text(row['cvd_thickness_nm'], 5, f"Fault\n{row['wafer_id']}", color='#d35400', weight='bold', ha='center', bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.3'))

plt.title('CVD Thickness Distribution with Isolated Chamber Anomalies', fontweight='bold')
plt.xlabel('Deposited CVD Layer Thickness [nm]')
plt.ylabel('Frequency [Wafer Count]')
plt.tight_layout()
plt.savefig("../figures/07_cvd_thickness_outliers.png", dpi=300)
plt.close()

print("\n[Success] Plots 06 and 07 saved to '../figures/'.")