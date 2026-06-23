import pandas as pd
import numpy as np
import os
eurostat = pd.read_csv("/Users/eugenmojsovic/Desktop/Teza/Raw/estat_nrg_ti_gas_en.csv")
eurostat["OBS_VALUE"] = (
    eurostat["OBS_VALUE"]
    .astype(str)
    .str.replace(".", "", regex=False)
    .astype(float))
eurostat = eurostat[eurostat["siec"].isin(["G3000"])]
eurostat = eurostat[eurostat["unit"].isin(["MIO_M3"])]
eurostat = eurostat[["partner","unit","geo","TIME_PERIOD","OBS_VALUE"]]
eurostat = eurostat[
    (eurostat["TIME_PERIOD"] >= 2019) &
    (eurostat["TIME_PERIOD"] <= 2021)]
eurostat = eurostat[eurostat["partner"].isin(["RU", "Russia", "Russian Federation", "TOTAL", "World", "WORLD"])]
eurostat = eurostat[eurostat["geo"].isin(["BG", "PL", "CZ", "HU", "SK","RO","SI"])]

year_map = {1:2024,2:2023,3:2022,4:2021,5:2020,6:2019,7:2018}
def map_nace_2digit(x):
    x = int(x)
    if 1 <= x <= 3:
        return "Agriculture"
    elif 5 <= x <= 9:
        return "Mining & energy"
    elif 10 <= x <= 33:
        return "Manufacturing"
    elif x == 35:
        return "Utilities"
    elif 41 <= x <= 43:
        return "Construction"
    elif 45 <= x <= 47:
        return "Trade"
    elif 49 <= x <= 53:
        return "Transport"
    elif 55 <= x <= 56:
        return "Accommodation & food"
    elif 58 <= x <= 63:
        return "ICT"
    elif 64 <= x <= 66:
        return "Finance & insurance"
    elif x == 68:
        return "Real estate"
    elif 69 <= x <= 75:
        return "Professional services"
    elif 84 <= x <= 88:
        return "Public & social services"
    else:
        return "Other"
def convert_year(col):
    import re
    match = re.search(r"Year - (\d+)", col)
    if match:
        rel = int(match.group(1))
        year = 2025 - rel
        return re.sub(r"Year - \d+", str(year), col)
    return col
def size_class(x):
    if pd.isna(x):
        return None
    elif x < 50:
        return "small"
    elif x < 250:
        return "medium"
    else:
        return "large"
     
BG_GAS_RU = eurostat[(eurostat["geo"] == "BG") & (eurostat["partner"] == "RU")]
BG_GAS_RU = BG_GAS_RU.set_index("TIME_PERIOD")
BG_GAS_TO = eurostat[(eurostat["geo"] == "BG") & (eurostat["partner"] == "TOTAL")]
BG_GAS_TO = BG_GAS_TO.set_index("TIME_PERIOD")
BG_l = BG_GAS_RU["OBS_VALUE"]/BG_GAS_TO["OBS_VALUE"]
BG_R = BG_l.mean()
orbis_BG = pd.read_csv(
    "/Users/eugenmojsovic/Desktop/Teza/Raw/data_BG.csv",
    keep_default_na=False)
orbis_BG = orbis_BG.replace(["N.A.", "n.a.", "NA", "na", ""], np.nan)
orbis_BG_clean = orbis_BG.dropna()
orbis_BG_filtered = orbis_BG_clean[orbis_BG_clean["Last avail. year"] == 2024]
orbis_BG_filtered = orbis_BG_filtered.apply(lambda col: pd.to_numeric(col.str.replace('.', '', regex=False), errors='coerce') if col.dtype == 'object' and col.name != 'Name' else col)
orbis_BG_filtered["ind"] = orbis_BG_filtered["NACE Rev. 2, core code (4 digits)"].astype(str).str[:2]
orbis_BG_filtered["ind"] = orbis_BG_filtered["ind"].apply(map_nace_2digit)
orbis_BG_filtered = orbis_BG_filtered[orbis_BG_filtered["ind"] != "Finance & insurance"]
orbis_BG_filtered = orbis_BG_filtered.drop(columns=["Last avail. year","NACE Rev. 2, core code (4 digits)"])
orbis_BG_filtered.columns = [convert_year(c) for c in orbis_BG_filtered.columns]
orbis_BG_filtered["country"] = "BG"
orbis_BG_filtered["gas"]=BG_R
for year in range(2024, 2018, -1):
    fa_y   = f"Tangible fixed assets EUR {year}"
    fa_y1  = f"Tangible fixed assets EUR {year - 1}"
    ta_y   = f"Total assets EUR {year}"
    col_name = f"investment_proxy_{year}"
    orbis_BG_filtered[col_name] = (
        (orbis_BG_filtered[fa_y] - orbis_BG_filtered[fa_y1]) /
        orbis_BG_filtered[ta_y])
    sg_col = f"sales_g {year}"
    rev_t = f"Operating revenue (Turnover) EUR {year}"
    rev_t1 = f"Operating revenue (Turnover) EUR {year - 1}"
    orbis_BG_filtered[sg_col] = (
        (orbis_BG_filtered[rev_t] - orbis_BG_filtered[rev_t1]) /
        orbis_BG_filtered[rev_t1])
    er_col = f"er {year}"
    sf_t = f"Shareholders funds EUR {year}"
    orbis_BG_filtered[er_col] = (
        orbis_BG_filtered[sf_t] /
        orbis_BG_filtered[ta_y])
orbis_BG_filtered["sales_g 2018"] = 0  
orbis_BG_filtered["investment_proxy_2018"] = 0
for year in range(2018, 2025):
    ebit_col = f"Operating profit (loss) [EBIT] EUR {year}"
    ta_col   = f"Total assets EUR {year}"
    prof_col = f"profitability {year}"
    orbis_BG_filtered[prof_col] = (
    orbis_BG_filtered[ebit_col] /
    orbis_BG_filtered[ta_col])
    size_col = f"Size {year}"
    orbis_BG_filtered[size_col] = np.log(orbis_BG_filtered[ta_col])   
orbis_BG_filtered = orbis_BG_filtered.replace([np.inf, -np.inf], np.nan)
orbis_BG_filtered = orbis_BG_filtered.dropna(subset=[size_col])
orbis_BG_filtered = (
    orbis_BG_filtered
    .nlargest(1000, size_col)
    .copy())
datasets_by_yearBG = {}
base_cols = ["Name", "country","gas",'ind']
for year in range(2019, 2025):
    year_cols = [
    f"Size {year}",
    f"profitability {year}",
    f"investment_proxy_{year}",
    f"sales_g {year}",
    f"er {year}"
    ]    
    cols_to_keep = base_cols + year_cols
    df_year = orbis_BG_filtered[cols_to_keep].copy()
    df_year["post"] = 1 if year >= 2022 else 0
    df_year["year"] = year
    df_year["post_gas"] = df_year["post"] * df_year["gas"]
    df_year = df_year.rename(columns=lambda c: (
    c.replace(f" {year}", "")
    if c.startswith(("Size", "profitability","sales_g","er"))
    else c.replace(f"_{year}", "")))
    datasets_by_yearBG[year] = df_year
BG_total = pd.concat(datasets_by_yearBG.values(), ignore_index=True)
 
PL_GAS_RU = eurostat[(eurostat["geo"] == "PL") & (eurostat["partner"] == "RU")]
PL_GAS_RU = PL_GAS_RU.set_index("TIME_PERIOD")
PL_GAS_TO = eurostat[(eurostat["geo"] == "PL") & (eurostat["partner"] == "TOTAL")]
PL_GAS_TO = PL_GAS_TO.set_index("TIME_PERIOD")
PL_l = PL_GAS_RU["OBS_VALUE"]/PL_GAS_TO["OBS_VALUE"]
PL_R = PL_l.mean()
orbis_PL = pd.read_csv(
    "/Users/eugenmojsovic/Desktop/Teza/Raw/data_PL.csv",
    keep_default_na=False)
orbis_PL = orbis_PL.replace(["N.A.", "n.a.", "NA", "na", ""], np.nan)
orbis_PL_clean = orbis_PL.dropna()
orbis_PL_filtered = orbis_PL_clean[orbis_PL_clean["Last avail. year"] == 2024]
orbis_PL_filtered = orbis_PL_filtered.apply(lambda col: pd.to_numeric(col.str.replace('.', '', regex=False), errors='coerce') if col.dtype == 'object' and col.name != 'Name' else col)
orbis_PL_filtered["ind"] = orbis_PL_filtered["NACE Rev. 2, core code (4 digits)"].astype(str).str[:2]
orbis_PL_filtered["ind"] = orbis_PL_filtered["ind"].apply(map_nace_2digit)
orbis_PL_filtered = orbis_PL_filtered[orbis_PL_filtered["ind"] != "Finance & insurance"]
orbis_PL_filtered = orbis_PL_filtered.drop(columns=["Last avail. year","NACE Rev. 2, core code (4 digits)"])
orbis_PL_filtered.columns = [convert_year(c) for c in orbis_PL_filtered.columns]
orbis_PL_filtered["country"] = "PL"
orbis_PL_filtered["gas"]=PL_R
for year in range(2024, 2018, -1):
    fa_y   = f"Tangible fixed assets EUR {year}"
    fa_y1  = f"Tangible fixed assets EUR {year - 1}"
    ta_y   = f"Total assets EUR {year}"
    col_name = f"investment_proxy_{year}"
    orbis_PL_filtered[col_name] = (
        (orbis_PL_filtered[fa_y] - orbis_PL_filtered[fa_y1]) /
        orbis_PL_filtered[ta_y])
    sg_col = f"sales_g {year}"
    rev_t = f"Operating revenue (Turnover) EUR {year}"
    rev_t1 = f"Operating revenue (Turnover) EUR {year - 1}"
    orbis_PL_filtered[sg_col] = (
        (orbis_PL_filtered[rev_t] - orbis_PL_filtered[rev_t1]) /
        orbis_PL_filtered[rev_t1])
    er_col = f"er {year}"
    sf_t = f"Shareholders funds EUR {year}"
    orbis_PL_filtered[er_col] = (
        orbis_PL_filtered[sf_t] /
        orbis_PL_filtered[ta_y])
orbis_PL_filtered["sales_g 2018"] = 0  
orbis_PL_filtered["investment_proxy_2018"] = 0
for year in range(2018, 2025):
    ebit_col = f"Operating profit (loss) [EBIT] EUR {year}"
    ta_col   = f"Total assets EUR {year}"
    prof_col = f"profitability {year}"
    orbis_PL_filtered[prof_col] = (
    orbis_PL_filtered[ebit_col] /
    orbis_PL_filtered[ta_col])
    size_col = f"Size {year}"
    orbis_PL_filtered[size_col] = np.log(orbis_PL_filtered[ta_col])   
orbis_PL_filtered = orbis_PL_filtered.replace([np.inf, -np.inf], np.nan)
orbis_PL_filtered = orbis_PL_filtered.dropna(subset=[size_col])
orbis_PL_filtered = (
    orbis_PL_filtered
    .nlargest(1000, size_col)
    .copy())
orbis_PL_filtered.loc[4495, "Name"] = "PRZEDSIEBIORSTWO WODOCIAGOW I KANALIZACJI SP. Z O.O. 2"
datasets_by_yearPL = {}
base_cols = ["Name", "country","gas",'ind']
for year in range(2019, 2025):
    year_cols = [
    f"Size {year}",
    f"profitability {year}",
    f"investment_proxy_{year}",
    f"sales_g {year}",
    f"er {year}"
    ]    
    cols_to_keep = base_cols + year_cols
    df_year = orbis_PL_filtered[cols_to_keep].copy()
    df_year["post"] = 1 if year >= 2022 else 0
    df_year["year"] = year
    df_year["post_gas"] = df_year["post"] * df_year["gas"]
    df_year = df_year.rename(columns=lambda c: (
    c.replace(f" {year}", "")
    if c.startswith(("Size", "profitability","sales_g","er"))
    else c.replace(f"_{year}", "")))
    datasets_by_yearPL[year] = df_year
PL_total = pd.concat(datasets_by_yearPL.values(), ignore_index=True)
 
CZ_GAS_RU = eurostat[(eurostat["geo"] == "CZ") & (eurostat["partner"] == "RU")]
CZ_GAS_RU = CZ_GAS_RU.set_index("TIME_PERIOD")
CZ_GAS_TO = eurostat[(eurostat["geo"] == "CZ") & (eurostat["partner"] == "TOTAL")]
CZ_GAS_TO = CZ_GAS_TO.set_index("TIME_PERIOD")
CZ_l = CZ_GAS_RU["OBS_VALUE"]/CZ_GAS_TO["OBS_VALUE"]
CZ_R = CZ_l.mean()
orbis_CZ = pd.read_csv(
    "/Users/eugenmojsovic/Desktop/Teza/Raw/data_CZ.csv",
    keep_default_na=False)
orbis_CZ = orbis_CZ.replace(["N.A.", "n.a.", "NA", "na", ""], np.nan)
orbis_CZ_clean = orbis_CZ.dropna()
orbis_CZ_filtered = orbis_CZ_clean[orbis_CZ_clean["Last avail. year"] == 2024]
orbis_CZ_filtered = orbis_CZ_filtered.apply(lambda col: pd.to_numeric(col.str.replace('.', '', regex=False), errors='coerce') if col.dtype == 'object' and col.name != 'Name' else col)
orbis_CZ_filtered["ind"] = orbis_CZ_filtered["NACE Rev. 2, core code (4 digits)"].astype(str).str[:2]
orbis_CZ_filtered["ind"] = orbis_CZ_filtered["ind"].apply(map_nace_2digit)
orbis_CZ_filtered = orbis_CZ_filtered[orbis_CZ_filtered["ind"] != "Finance & insurance"]
orbis_CZ_filtered = orbis_CZ_filtered.drop(columns=["Last avail. year","NACE Rev. 2, core code (4 digits)"])
orbis_CZ_filtered.columns = [convert_year(c) for c in orbis_CZ_filtered.columns]
orbis_CZ_filtered["country"] = "CZ"
orbis_CZ_filtered["gas"]=CZ_R
for year in range(2024, 2018, -1):
    fa_y   = f"Tangible fixed assets EUR {year}"
    fa_y1  = f"Tangible fixed assets EUR {year - 1}"
    ta_y   = f"Total assets EUR {year}"
    col_name = f"investment_proxy_{year}"
    orbis_CZ_filtered[col_name] = (
        (orbis_CZ_filtered[fa_y] - orbis_CZ_filtered[fa_y1]) /
        orbis_CZ_filtered[ta_y])
    sg_col = f"sales_g {year}"
    rev_t = f"Operating revenue (Turnover) EUR {year}"
    rev_t1 = f"Operating revenue (Turnover) EUR {year - 1}"
    orbis_CZ_filtered[sg_col] = (
        (orbis_CZ_filtered[rev_t] - orbis_CZ_filtered[rev_t1]) /
        orbis_CZ_filtered[rev_t1])
    er_col = f"er {year}"
    sf_t = f"Shareholders funds EUR {year}"
    orbis_CZ_filtered[er_col] = (
        orbis_CZ_filtered[sf_t] /
        orbis_CZ_filtered[ta_y])
orbis_CZ_filtered["sales_g 2018"] = 0  
orbis_CZ_filtered["investment_proxy_2018"] = 0
for year in range(2018, 2025):
    ebit_col = f"Operating profit (loss) [EBIT] EUR {year}"
    ta_col   = f"Total assets EUR {year}"
    prof_col = f"profitability {year}"
    orbis_CZ_filtered[prof_col] = (
    orbis_CZ_filtered[ebit_col] /
    orbis_CZ_filtered[ta_col])
    size_col = f"Size {year}"
    orbis_CZ_filtered[size_col] = np.log(orbis_CZ_filtered[ta_col])   
orbis_CZ_filtered = orbis_CZ_filtered.replace([np.inf, -np.inf], np.nan)
orbis_CZ_filtered = orbis_CZ_filtered.dropna(subset=[size_col])
orbis_CZ_filtered = (
    orbis_CZ_filtered
    .nlargest(1000, size_col)
    .copy())
orbis_CZ_filtered.loc[
    orbis_CZ_filtered["Name"] == "P AUTOMOBIL IMPORT S.R.O.",
    "Name"
] = "P AUTOMOBIL IMPORT S.R.O. CZ"
datasets_by_yearCZ = {}
base_cols = ["Name", "country","gas",'ind']
for year in range(2019, 2025):
    year_cols = [
    f"Size {year}",
    f"profitability {year}",
    f"investment_proxy_{year}",
    f"sales_g {year}",
    f"er {year}"
    ]    
    cols_to_keep = base_cols + year_cols
    df_year = orbis_CZ_filtered[cols_to_keep].copy()
    df_year["post"] = 1 if year >= 2022 else 0
    df_year["year"] = year
    df_year["post_gas"] = df_year["post"] * df_year["gas"]
    df_year = df_year.rename(columns=lambda c: (
    c.replace(f" {year}", "")
    if c.startswith(("Size", "profitability","sales_g","er"))
    else c.replace(f"_{year}", "")))
    datasets_by_yearCZ[year] = df_year
CZ_total = pd.concat(datasets_by_yearCZ.values(), ignore_index=True)
 
HU_GAS_RU = eurostat[(eurostat["geo"] == "HU") & (eurostat["partner"] == "RU")]
HU_GAS_RU = HU_GAS_RU.set_index("TIME_PERIOD")
HU_GAS_TO = eurostat[(eurostat["geo"] == "HU") & (eurostat["partner"] == "TOTAL")]
HU_GAS_TO = HU_GAS_TO.set_index("TIME_PERIOD")
HU_l = HU_GAS_RU["OBS_VALUE"]/HU_GAS_TO["OBS_VALUE"]
HU_R = HU_l.mean()
orbis_HU = pd.read_csv(
    "/Users/eugenmojsovic/Desktop/Teza/Raw/data_HU.csv",
    keep_default_na=False)
orbis_HU = orbis_HU.replace(["N.A.", "n.a.", "NA", "na", ""], np.nan)
orbis_HU_clean = orbis_HU.dropna()
orbis_HU_filtered = orbis_HU_clean[orbis_HU_clean["Last avail. year"] == 2024]
orbis_HU_filtered = orbis_HU_filtered.apply(lambda col: pd.to_numeric(col.str.replace('.', '', regex=False), errors='coerce') if col.dtype == 'object' and col.name != 'Name' else col)
orbis_HU_filtered["ind"] = orbis_HU_filtered["NACE Rev. 2, core code (4 digits)"].astype(str).str[:2]
orbis_HU_filtered["ind"] = orbis_HU_filtered["ind"].apply(map_nace_2digit)
orbis_HU_filtered = orbis_HU_filtered[orbis_HU_filtered["ind"] != "Finance & insurance"]
orbis_HU_filtered = orbis_HU_filtered.drop(columns=["Last avail. year","NACE Rev. 2, core code (4 digits)"])
orbis_HU_filtered.columns = [convert_year(c) for c in orbis_HU_filtered.columns]
orbis_HU_filtered["country"] = "HU"
orbis_HU_filtered["gas"]=HU_R
for year in range(2024, 2018, -1):
    fa_y   = f"Tangible fixed assets EUR {year}"
    fa_y1  = f"Tangible fixed assets EUR {year - 1}"
    ta_y   = f"Total assets EUR {year}"
    col_name = f"investment_proxy_{year}"
    orbis_HU_filtered[col_name] = (
        (orbis_HU_filtered[fa_y] - orbis_HU_filtered[fa_y1]) /
        orbis_HU_filtered[ta_y])
    sg_col = f"sales_g {year}"
    rev_t = f"Operating revenue (Turnover) EUR {year}"
    rev_t1 = f"Operating revenue (Turnover) EUR {year - 1}"
    orbis_HU_filtered[sg_col] = (
        (orbis_HU_filtered[rev_t] - orbis_HU_filtered[rev_t1]) /
        orbis_HU_filtered[rev_t1])
    er_col = f"er {year}"
    sf_t = f"Shareholders funds EUR {year}"
    orbis_HU_filtered[er_col] = (
        orbis_HU_filtered[sf_t] /
        orbis_HU_filtered[ta_y])
orbis_HU_filtered["sales_g 2018"] = 0  
orbis_HU_filtered["investment_proxy_2018"] = 0
for year in range(2018, 2025):
    ebit_col = f"Operating profit (loss) [EBIT] EUR {year}"
    ta_col   = f"Total assets EUR {year}"
    prof_col = f"profitability {year}"
    orbis_HU_filtered[prof_col] = (
    orbis_HU_filtered[ebit_col] /
    orbis_HU_filtered[ta_col])
    size_col = f"Size {year}"
    orbis_HU_filtered[size_col] = np.log(orbis_HU_filtered[ta_col])   
orbis_HU_filtered = orbis_HU_filtered.replace([np.inf, -np.inf], np.nan)
orbis_HU_filtered = orbis_HU_filtered.dropna(subset=[size_col])
orbis_HU_filtered = (
    orbis_HU_filtered
    .nlargest(1000, size_col)
    .copy())
datasets_by_yearHU = {}
base_cols = ["Name", "country","gas",'ind']
for year in range(2019, 2025):
    year_cols = [
    f"Size {year}",
    f"profitability {year}",
    f"investment_proxy_{year}",
    f"sales_g {year}",
    f"er {year}"
    ]    
    cols_to_keep = base_cols + year_cols
    df_year = orbis_HU_filtered[cols_to_keep].copy()
    df_year["post"] = 1 if year >= 2022 else 0
    df_year["year"] = year
    df_year["post_gas"] = df_year["post"] * df_year["gas"]
    df_year = df_year.rename(columns=lambda c: (
    c.replace(f" {year}", "")
    if c.startswith(("Size", "profitability","sales_g","er"))
    else c.replace(f"_{year}", "")))
    datasets_by_yearHU[year] = df_year
HU_total = pd.concat(datasets_by_yearHU.values(), ignore_index=True)
 
RO_GAS_RU = eurostat[(eurostat["geo"] == "RO") & (eurostat["partner"] == "RU")]
RO_GAS_RU = RO_GAS_RU.set_index("TIME_PERIOD")
RO_GAS_TO = eurostat[(eurostat["geo"] == "RO") & (eurostat["partner"] == "TOTAL")]
RO_GAS_TO = RO_GAS_TO.set_index("TIME_PERIOD")
RO_l = RO_GAS_RU["OBS_VALUE"]/RO_GAS_TO["OBS_VALUE"]
RO_R = RO_l.mean()
orbis_RO = pd.read_csv(
    "/Users/eugenmojsovic/Desktop/Teza/Raw/data_RO.csv",
    keep_default_na=False)
orbis_RO = orbis_RO.replace(["N.A.", "n.a.", "NA", "na", ""], np.nan)
orbis_RO_clean = orbis_RO.dropna()
orbis_RO_filtered = orbis_RO_clean[orbis_RO_clean["Last avail. year"] == 2024]
orbis_RO_filtered = orbis_RO_filtered.apply(lambda col: pd.to_numeric(col.str.replace('.', '', regex=False), errors='coerce') if col.dtype == 'object' and col.name != 'Name' else col)
orbis_RO_filtered["ind"] = orbis_RO_filtered["NACE Rev. 2, core code (4 digits)"].astype(str).str[:2]
orbis_RO_filtered["ind"] = orbis_RO_filtered["ind"].apply(map_nace_2digit)
orbis_RO_filtered = orbis_RO_filtered[orbis_RO_filtered["ind"] != "Finance & insurance"]
orbis_RO_filtered = orbis_RO_filtered.drop(columns=["Last avail. year","NACE Rev. 2, core code (4 digits)"])
orbis_RO_filtered.columns = [convert_year(c) for c in orbis_RO_filtered.columns]
orbis_RO_filtered["country"] = "RO"
orbis_RO_filtered["gas"]=RO_R
for year in range(2024, 2018, -1):
    fa_y   = f"Tangible fixed assets EUR {year}"
    fa_y1  = f"Tangible fixed assets EUR {year - 1}"
    ta_y   = f"Total assets EUR {year}"
    col_name = f"investment_proxy_{year}"
    orbis_RO_filtered[col_name] = (
        (orbis_RO_filtered[fa_y] - orbis_RO_filtered[fa_y1]) /
        orbis_RO_filtered[ta_y])
    sg_col = f"sales_g {year}"
    rev_t = f"Operating revenue (Turnover) EUR {year}"
    rev_t1 = f"Operating revenue (Turnover) EUR {year - 1}"
    orbis_RO_filtered[sg_col] = (
        (orbis_RO_filtered[rev_t] - orbis_RO_filtered[rev_t1]) /
        orbis_RO_filtered[rev_t1])
    er_col = f"er {year}"
    sf_t = f"Shareholders funds EUR {year}"
    orbis_RO_filtered[er_col] = (
        orbis_RO_filtered[sf_t] /
        orbis_RO_filtered[ta_y])
orbis_RO_filtered["sales_g 2018"] = 0  
orbis_RO_filtered["investment_proxy_2018"] = 0
for year in range(2018, 2025):
    ebit_col = f"Operating profit (loss) [EBIT] EUR {year}"
    ta_col   = f"Total assets EUR {year}"
    prof_col = f"profitability {year}"
    orbis_RO_filtered[prof_col] = (
    orbis_RO_filtered[ebit_col] /
    orbis_RO_filtered[ta_col])
    size_col = f"Size {year}"
    orbis_RO_filtered[size_col] = np.log(orbis_RO_filtered[ta_col])   
orbis_RO_filtered = orbis_RO_filtered.replace([np.inf, -np.inf], np.nan)
orbis_RO_filtered = orbis_RO_filtered.dropna(subset=[size_col])
orbis_RO_filtered = (
    orbis_RO_filtered
    .nlargest(1000, size_col)
    .copy())
datasets_by_yearRO = {}
base_cols = ["Name", "country","gas",'ind']
for year in range(2019, 2025):
    year_cols = [
    f"Size {year}",
    f"profitability {year}",
    f"investment_proxy_{year}",
    f"sales_g {year}",
    f"er {year}"
    ]    
    cols_to_keep = base_cols + year_cols
    df_year = orbis_RO_filtered[cols_to_keep].copy()
    df_year["post"] = 1 if year >= 2022 else 0
    df_year["year"] = year
    df_year["post_gas"] = df_year["post"] * df_year["gas"]
    df_year = df_year.rename(columns=lambda c: (
    c.replace(f" {year}", "")
    if c.startswith(("Size", "profitability","sales_g","er"))
    else c.replace(f"_{year}", "")))
    datasets_by_yearRO[year] = df_year
RO_total = pd.concat(datasets_by_yearRO.values(), ignore_index=True)
 
SK_GAS_RU = eurostat[(eurostat["geo"] == "SK") & (eurostat["partner"] == "RU")]
SK_GAS_RU = SK_GAS_RU.set_index("TIME_PERIOD")
SK_GAS_TO = eurostat[(eurostat["geo"] == "SK") & (eurostat["partner"] == "TOTAL")]
SK_GAS_TO = SK_GAS_TO.set_index("TIME_PERIOD")
SK_l = SK_GAS_RU["OBS_VALUE"]/SK_GAS_TO["OBS_VALUE"]
SK_R = SK_l.mean()
orbis_SK = pd.read_csv(
    "/Users/eugenmojsovic/Desktop/Teza/Raw/data_SK.csv",
    keep_default_na=False)
orbis_SK = orbis_SK.replace(["N.A.", "n.a.", "NA", "na", ""], np.nan)
orbis_SK_clean = orbis_SK.dropna()
orbis_SK_filtered = orbis_SK_clean[orbis_SK_clean["Last avail. year"] == 2024]
orbis_SK_filtered = orbis_SK_filtered.apply(lambda col: pd.to_numeric(col.str.replace('.', '', regex=False), errors='coerce') if col.dtype == 'object' and col.name != 'Name' else col)
orbis_SK_filtered["ind"] = orbis_SK_filtered["NACE Rev. 2, core code (4 digits)"].astype(str).str[:2]
orbis_SK_filtered["ind"] = orbis_SK_filtered["ind"].apply(map_nace_2digit)
orbis_SK_filtered = orbis_SK_filtered[orbis_SK_filtered["ind"] != "Finance & insurance"]
orbis_SK_filtered = orbis_SK_filtered.drop(columns=["Last avail. year","NACE Rev. 2, core code (4 digits)"])
orbis_SK_filtered.columns = [convert_year(c) for c in orbis_SK_filtered.columns]
orbis_SK_filtered["country"] = "SK"
orbis_SK_filtered["gas"]=SK_R
for year in range(2024, 2018, -1):
    fa_y   = f"Tangible fixed assets EUR {year}"
    fa_y1  = f"Tangible fixed assets EUR {year - 1}"
    ta_y   = f"Total assets EUR {year}"
    col_name = f"investment_proxy_{year}"
    orbis_SK_filtered[col_name] = (
        (orbis_SK_filtered[fa_y] - orbis_SK_filtered[fa_y1]) /
        orbis_SK_filtered[ta_y])
    sg_col = f"sales_g {year}"
    rev_t = f"Operating revenue (Turnover) EUR {year}"
    rev_t1 = f"Operating revenue (Turnover) EUR {year - 1}"
    orbis_SK_filtered[sg_col] = (
        (orbis_SK_filtered[rev_t] - orbis_SK_filtered[rev_t1]) /
        orbis_SK_filtered[rev_t1])
    er_col = f"er {year}"
    sf_t = f"Shareholders funds EUR {year}"
    orbis_SK_filtered[er_col] = (
        orbis_SK_filtered[sf_t] /
        orbis_SK_filtered[ta_y])
orbis_SK_filtered["sales_g 2018"] = 0  
orbis_SK_filtered["investment_proxy_2018"] = 0
for year in range(2018, 2025):
    ebit_col = f"Operating profit (loss) [EBIT] EUR {year}"
    ta_col   = f"Total assets EUR {year}"
    prof_col = f"profitability {year}"
    orbis_SK_filtered[prof_col] = (
    orbis_SK_filtered[ebit_col] /
    orbis_SK_filtered[ta_col])
    size_col = f"Size {year}"
    orbis_SK_filtered[size_col] = np.log(orbis_SK_filtered[ta_col])   
orbis_SK_filtered = orbis_SK_filtered.replace([np.inf, -np.inf], np.nan)
orbis_SK_filtered = orbis_SK_filtered.dropna(subset=[size_col])
orbis_SK_filtered = (
    orbis_SK_filtered
    .nlargest(1000, size_col)
    .copy())
datasets_by_yearSK = {}
base_cols = ["Name", "country","gas",'ind']
for year in range(2019, 2025):
    year_cols = [
    f"Size {year}",
    f"profitability {year}",
    f"investment_proxy_{year}",
    f"sales_g {year}",
    f"er {year}"
    ]    
    cols_to_keep = base_cols + year_cols
    df_year = orbis_SK_filtered[cols_to_keep].copy()
    df_year["post"] = 1 if year >= 2022 else 0
    df_year["year"] = year
    df_year["post_gas"] = df_year["post"] * df_year["gas"]
    df_year = df_year.rename(columns=lambda c: (
    c.replace(f" {year}", "")
    if c.startswith(("Size", "profitability","sales_g","er"))
    else c.replace(f"_{year}", "")))
    datasets_by_yearSK[year] = df_year
SK_total = pd.concat(datasets_by_yearSK.values(), ignore_index=True)
 
SI_GAS_RU = eurostat[(eurostat["geo"] == "SI") & (eurostat["partner"] == "RU")]
SI_GAS_RU = SI_GAS_RU.set_index("TIME_PERIOD")
SI_GAS_TO = eurostat[(eurostat["geo"] == "SI") & (eurostat["partner"] == "TOTAL")]
SI_GAS_TO = SI_GAS_TO.set_index("TIME_PERIOD")
SI_l = SI_GAS_RU["OBS_VALUE"]/SI_GAS_TO["OBS_VALUE"]
SI_R = SI_l.mean()
orbis_SI = pd.read_csv(
    "/Users/eugenmojsovic/Desktop/Teza/Raw/data_SI.csv",
    keep_default_na=False)
orbis_SI = orbis_SI.replace(["N.A.", "n.a.", "NA", "na", ""], np.nan)
orbis_SI_clean = orbis_SI.dropna()
orbis_SI_filtered = orbis_SI_clean[orbis_SI_clean["Last avail. year"] == 2024]
orbis_SI_filtered = orbis_SI_filtered.apply(lambda col: pd.to_numeric(col.str.replace('.', '', regex=False), errors='coerce') if col.dtype == 'object' and col.name != 'Name' else col)
orbis_SI_filtered["ind"] = orbis_SI_filtered["NACE Rev. 2, core code (4 digits)"].astype(str).str[:2]
orbis_SI_filtered["ind"] = orbis_SI_filtered["ind"].apply(map_nace_2digit)
orbis_SI_filtered = orbis_SI_filtered[orbis_SI_filtered["ind"] != "Finance & insurance"]
orbis_SI_filtered = orbis_SI_filtered.drop(columns=["Last avail. year","NACE Rev. 2, core code (4 digits)"])
orbis_SI_filtered.columns = [convert_year(c) for c in orbis_SI_filtered.columns]
orbis_SI_filtered["country"] = "SI"
orbis_SI_filtered["gas"]=SI_R
for year in range(2024, 2018, -1):
    fa_y   = f"Tangible fixed assets EUR {year}"
    fa_y1  = f"Tangible fixed assets EUR {year - 1}"
    ta_y   = f"Total assets EUR {year}"
    col_name = f"investment_proxy_{year}"
    orbis_SI_filtered[col_name] = (
        (orbis_SI_filtered[fa_y] - orbis_SI_filtered[fa_y1]) /
        orbis_SI_filtered[ta_y])
    sg_col = f"sales_g {year}"
    rev_t = f"Operating revenue (Turnover) EUR {year}"
    rev_t1 = f"Operating revenue (Turnover) EUR {year - 1}"
    orbis_SI_filtered[sg_col] = (
        (orbis_SI_filtered[rev_t] - orbis_SI_filtered[rev_t1]) /
        orbis_SI_filtered[rev_t1])
    er_col = f"er {year}"
    sf_t = f"Shareholders funds EUR {year}"
    orbis_SI_filtered[er_col] = (
        orbis_SI_filtered[sf_t] /
        orbis_SI_filtered[ta_y])
orbis_SI_filtered["sales_g 2018"] = 0  
orbis_SI_filtered["investment_proxy_2018"] = 0
for year in range(2018, 2025):
    ebit_col = f"Operating profit (loss) [EBIT] EUR {year}"
    ta_col   = f"Total assets EUR {year}"
    prof_col = f"profitability {year}"
    orbis_SI_filtered[prof_col] = (
    orbis_SI_filtered[ebit_col] /
    orbis_SI_filtered[ta_col])
    size_col = f"Size {year}"
    orbis_SI_filtered[size_col] = np.log(orbis_SI_filtered[ta_col])   
orbis_SI_filtered = orbis_SI_filtered.replace([np.inf, -np.inf], np.nan)
orbis_SI_filtered = orbis_SI_filtered.dropna(subset=[size_col])
orbis_SI_filtered = (
    orbis_SI_filtered
    .nlargest(1000, size_col)
    .copy())
datasets_by_yearSI = {}
base_cols = ["Name", "country","gas",'ind']
for year in range(2019, 2025):
    year_cols = [
    f"Size {year}",
    f"profitability {year}",
    f"investment_proxy_{year}",
    f"sales_g {year}",
    f"er {year}"
    ]    
    cols_to_keep = base_cols + year_cols
    df_year = orbis_SI_filtered[cols_to_keep].copy()
    df_year["post"] = 1 if year >= 2023 else 0
    df_year["year"] = year
    df_year["post_gas"] = df_year["post"] * df_year["gas"]
    df_year = df_year.rename(columns=lambda c: (
    c.replace(f" {year}", "")
    if c.startswith(("Size", "profitability","sales_g","er"))
    else c.replace(f"_{year}", "")))
    datasets_by_yearSI[year] = df_year
SI_total = pd.concat(datasets_by_yearSI.values(), ignore_index=True)
 
    
all_datasets = [BG_total, PL_total, CZ_total, RO_total, SK_total, SI_total, HU_total]
rfr = pd.concat(all_datasets, ignore_index=True)
rfr["Alternative"] = rfr["country"].isin(["PL", "BG", "RO"]).astype(int)
rfr = rfr.fillna(0)
file_path = os.path.join("/Users/eugenmojsovic/Desktop/Teza/", "CleanRobust1.csv")
rfr.to_csv(file_path, index=False)
    
    
    


























