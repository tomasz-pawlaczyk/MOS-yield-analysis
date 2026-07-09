import pandas as pd
import numpy as np

# Ustawienie ziarna losowości dla powtarzalności
np.random.seed(42)

n_wafers = 1000
wafer_ids = [f"WFR_{i:04d}" for i in range(1, n_wafers + 1)]
lot_ids = [f"LOT_{((i-1)//25)+1:03d}" for i in range(1, n_wafers + 1)]

# 1. Generowanie danych bazowych (proces w normie)
oxidation_temp = np.random.normal(1000, 3, n_wafers)
oxidation_time = np.random.normal(3600, 15, n_wafers)
# Grubość tlenku zależy od temperatury i czasu + szum
oxide_thickness = 100 + 0.15 * (oxidation_temp - 1000) + 0.02 * (oxidation_time - 3600) + np.random.normal(0, 1.0, n_wafers)

litho_alignment = np.abs(np.random.normal(15, 4, n_wafers))
exposure_dose = np.random.normal(220, 5, n_wafers)
focus_offset = np.random.normal(0.0, 0.02, n_wafers)
particle_count = np.random.poisson(3, n_wafers)

etch_time = np.random.normal(180, 4, n_wafers)
# Głębokość trawienia zależy od czasu trawienia, ale napotyka opór przy grubszym tlenku
etch_depth = 150 + 0.5 * (etch_time - 180) - 0.2 * (oxide_thickness - 100) + np.random.normal(0, 1.5, n_wafers)

cvd_thickness = np.random.normal(250, 6, n_wafers)
metal_thickness = np.random.normal(400, 10, n_wafers)

# Parametry elektryczne fizycznie skorelowane
line_resistance = 1.25 + 0.004 * (400 - metal_thickness) + 0.003 * (150 - etch_depth) + np.random.normal(0, 0.02, n_wafers)
leakage_current = np.random.lognormal(mean=1.3, sigma=0.25, size=n_wafers)
threshold_voltage = 0.65 + 0.012 * (oxide_thickness - 100) + np.random.normal(0, 0.015, n_wafers)

# =======================================================
# 2. WSTRZYKIWANIE ANOMALII (Zgodnie ze scenariuszem)
# =======================================================

# Scenariusz 1: Wafle 651-720 - Dryf temperatury na Oxidation i efekt domina
idx_scen1 = range(650, 720)
oxidation_temp[idx_scen1] += np.random.normal(18, 2, len(idx_scen1))
oxide_thickness[idx_scen1] = 100 + 0.15 * (oxidation_temp[idx_scen1] - 1000) + 0.02 * (oxidation_time[idx_scen1] - 3600) + np.random.normal(0, 0.8, len(idx_scen1))
threshold_voltage[idx_scen1] = 0.65 + 0.012 * (oxide_thickness[idx_scen1] - 100) + np.random.normal(0, 0.015, len(idx_scen1))
etch_time[idx_scen1] += np.random.normal(25, 3, len(idx_scen1))
etch_depth[idx_scen1] = 150 + 0.5 * (etch_time[idx_scen1] - 180) - 0.2 * (oxide_thickness[idx_scen1] - 100) + np.random.normal(0, 1.2, len(idx_scen1))
line_resistance[idx_scen1] += np.random.normal(0.35, 0.04, len(idx_scen1))

# Scenariusz 2: Wafle 800-850 - Zanieczyszczenie cząstkami (tylko część powoduje przebicia)
idx_scen2 = range(799, 850)
particle_count[idx_scen2] = np.random.poisson(42, len(idx_scen2))
corrupted_subset = np.random.choice(list(idx_scen2), size=20, replace=False)
leakage_current[corrupted_subset] *= np.random.uniform(15, 35, len(corrupted_subset))
line_resistance[corrupted_subset] += np.random.uniform(0.5, 1.8, len(corrupted_subset))

# Scenariusz 3: Pojedyncze Outliery (Ukryte błędy krytyczne)
line_resistance[122] = 14.85
cvd_thickness[455] = 112.4
cvd_thickness[788] = 438.1

outlier_leakage_idx = [54, 233, 511, 776, 910]
for idx in outlier_leakage_idx:
    leakage_current[idx] = np.random.uniform(550, 850)

# =======================================================
# 3. ZAPIS DO DATAFRAME
# =======================================================
df = pd.DataFrame({
    "wafer_id": wafer_ids,
    "lot_id": lot_ids,
    "oxidation_temp_c": np.round(oxidation_temp, 1),
    "oxidation_time_s": np.round(oxidation_time, 0).astype(int),
    "oxide_thickness_nm": np.round(oxide_thickness, 2),
    "lithography_alignment_nm": np.round(litho_alignment, 2),
    "exposure_dose_mj_cm2": np.round(exposure_dose, 1),
    "focus_offset_um": np.round(focus_offset, 3),
    "particle_count": particle_count,
    "etch_time_s": np.round(etch_time, 0).astype(int),
    "etch_depth_nm": np.round(etch_depth, 2),
    "cvd_thickness_nm": np.round(cvd_thickness, 2),
    "metal_thickness_nm": np.round(metal_thickness, 2),
    "line_resistance_ohm": np.round(line_resistance, 3),
    "leakage_current_na": np.round(leakage_current, 2),
    "threshold_voltage_v": np.round(threshold_voltage, 3)
})

# Zapis (użyto biblioteki openpyxl do wygenerowania załączonego pliku)
df.to_csv("wafer_fab_data_raw.csv", index=False)