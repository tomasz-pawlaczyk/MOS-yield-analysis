import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

os.makedirs("../figures", exist_ok=True)

print("Loading dataset from ../data/wafer_fab_data_raw.csv...")
df = pd.read_csv("../data/wafer_fab_data_raw.csv")

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
df['wafer_num'] = df['wafer_id'].str.extract(r'(\d+)').astype(int)

print("Generating Plot 1: Oxidation process stability...")
fig, ax1 = plt.subplots(figsize=(12, 5))

color1 = '#e74c3c'
ax1.set_xlabel('Wafer Number (Wafer ID)')
ax1.set_ylabel('Oxidation Temperature [°C]', color=color1, fontweight='bold')
sns.lineplot(data=df, x='wafer_num', y='oxidation_temp_c', ax=ax1, color=color1, alpha=0.7)
ax1.tick_params(axis='y', labelcolor=color1)

ax2 = ax1.twinx()
color2 = '#2980b9'
ax2.set_ylabel('Oxide Thickness (d_ox) [nm]', color=color2, fontweight='bold')
sns.lineplot(data=df, x='wafer_num', y='oxide_thickness_nm', ax=ax2, color=color2, alpha=0.7)
ax2.tick_params(axis='y', labelcolor=color2)

ax1.axvspan(650, 720, color='gray', alpha=0.2, label='Anomalous Drift Zone')
fig.suptitle('Process Disturbance: Furnace Temperature Spike vs Oxide Thickness', fontsize=14, fontweight='bold')
fig.tight_layout()
plt.savefig("../figures/01_process_drift.png", dpi=300)
plt.close()

print("Generating Plot 2: Temperature vs Threshold Voltage correlation...")
df['is_anomalous'] = np.where((df['wafer_num'] >= 650) & (df['wafer_num'] <= 720), 'Anomalous Batch', 'Normal')

plt.figure(figsize=(9, 6))
sns.scatterplot(
    data=df,
    x='oxidation_temp_c',
    y='threshold_voltage_v',
    hue='is_anomalous',
    palette={'Normal': '#27ae60', 'Anomalous Batch': '#c0392b'},
    alpha=0.6,
    edgecolor=None
)
plt.title('Impact of Oxidation Temperature on Threshold Voltage (V_th)', fontweight='bold')
plt.xlabel('Oxidation Temperature [°C]')
plt.ylabel('Threshold Voltage (V_th) [V]')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(title='Wafer Status')
plt.tight_layout()
plt.savefig("../figures/02_temp_vs_vth.png", dpi=300)
plt.close()

print("Generating Plot 3: Domino effect (Etch Time vs Line Resistance)...")
plt.figure(figsize=(9, 6))
sns.scatterplot(
    data=df,
    x='etch_time_s',
    y='line_resistance_ohm',
    hue='is_anomalous',
    palette={'Normal': '#8e44ad', 'Anomalous Batch': '#f39c12'},
    alpha=0.6,
    edgecolor=None
)

plt.title('Over-etch Domino Effect: Etch Time vs Line Resistance', fontweight='bold')
plt.xlabel('Plasma Etching Time [s]')
plt.ylabel('Line Resistance (R) [Ohm]')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(title='Wafer Status')
plt.tight_layout()
plt.savefig("../figures/03_domino_effect_etch_res.png", dpi=300)
plt.close()

print("\nSuccess! Plots 01, 02, and 03 saved to '../figures/'.")