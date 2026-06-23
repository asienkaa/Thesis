
import pandas as pd
import numpy as np
from scipy.stats.mstats import winsorize
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
    (eurostat["TIME_PERIOD"] == 2019)]
eurostat = eurostat[eurostat["partner"].isin(["RU", "Russia", "Russian Federation", "TOTAL", "World", "WORLD"])]
eurostat = eurostat[eurostat["geo"].isin(["BG", "PL", "CZ", "HU", "SK","RO","SI"])]

# =============================================================================
# PL 
# =============================================================================
PL = pd.read_csv("/Users/eugenmojsovic/Desktop/Teza/CapitalIQ/PL.csv")
bad_gvkeys = PL.loc[PL.isna().any(axis=1), 'gvkey'].unique()
PL = PL[~PL['gvkey'].isin(bad_gvkeys)]
bad_gvkeys = PL.loc[PL["at"] < 10, 'gvkey'].unique()
PL = PL[~PL['gvkey'].isin(bad_gvkeys)]
PL["Name"] = PL["gvkey"]
PL["country"] = "PL"
PL["ind"] = PL["sic"].astype(str).str[:2]
PL["ind"] = PL["ind"].apply(map_nace_2digit)
PL = PL[PL["ind"] != "Finance & insurance"]
PL["size"] = np.log(PL["at"])
PL["er"] = PL["teq"] / PL["at"]
PL['year'] = pd.to_datetime(PL['datadate']).dt.year
PL = PL[PL["year"] != 2025]
counts = PL['Name'].value_counts()
valid_names = counts[counts == 7].index
PL = PL[PL['Name'].isin(valid_names)]
PL["profitability"] = PL["ebit"] / PL['at']
PL["post"] = (PL["year"] >= 2022).astype(int)
PL2 = PL.sort_values(["Name", "year"]).copy()
PL2["lagged_revenue"] = PL2.groupby("Name")["revt"].shift(1)
PL["sales_growth"] = (
    (PL2["revt"] - PL2["lagged_revenue"]) / PL2["lagged_revenue"])
PL['cc'] = (
    (PL['capx'] - PL.groupby('Name')['capx'].shift(1))
    / PL.groupby('Name')['at'].shift(1)
)
PL = PL.drop(columns=['costat', 'datafmt',"indfmt","consol","fic","gvkey","sic", "datadate","at","ebit","revt","teq","capx"])
PL = PL[PL["year"] != 2018]
bad_gvkeys = PL.loc[PL.isna().any(axis=1), 'Name'].unique()
PL = PL[~PL['Name'].isin(bad_gvkeys)]
PL_GAS_RU = eurostat[(eurostat["geo"] == "PL") & (eurostat["partner"] == "RU")]
PL_GAS_RU = PL_GAS_RU.set_index("TIME_PERIOD")
PL_GAS_TO = eurostat[(eurostat["geo"] == "PL") & (eurostat["partner"] == "TOTAL")]
PL_GAS_TO = PL_GAS_TO.set_index("TIME_PERIOD")
PL_gas = PL_GAS_RU["OBS_VALUE"]/PL_GAS_TO["OBS_VALUE"]
PL["gas"] = float(PL_gas.iloc[0])
PL["post_gas"] = PL["gas"] * PL["post"]
PL["Alternative"] = 1
# =============================================================================
# RO
# =============================================================================
RO = pd.read_csv("/Users/eugenmojsovic/Desktop/Teza/CapitalIQ/RO.csv")
bad_gvkeys = RO.loc[RO.isna().any(axis=1), 'gvkey'].unique()
RO = RO[~RO['gvkey'].isin(bad_gvkeys)]
bad_gvkeys = RO.loc[RO["at"] < 10, 'gvkey'].unique()
RO = RO[~RO['gvkey'].isin(bad_gvkeys)]
RO["Name"] = RO["gvkey"]
RO["country"] = "RO"
RO["ind"] = RO["sic"].astype(str).str[:2]
RO["ind"] = RO["ind"].apply(map_nace_2digit)
RO = RO[RO["ind"] != "Finance & insurance"]
RO["size"] = np.log(RO["at"])
RO["er"] = RO["teq"] / RO["at"]
RO['year'] = pd.to_datetime(RO['datadate']).dt.year
RO = RO[RO["year"] != 2025]
counts = RO['Name'].value_counts()
valid_names = counts[counts == 7].index
RO = RO[RO['Name'].isin(valid_names)]
RO["profitability"] = RO["ebit"] / RO['at']
RO["post"] = (RO["year"] >= 2022).astype(int)
RO2 = RO.sort_values(["Name", "year"]).copy()
RO2["lagged_revenue"] = RO2.groupby("Name")["revt"].shift(1)
RO["sales_growth"] = (
    (RO2["revt"] - RO2["lagged_revenue"]) / RO2["lagged_revenue"])
RO['cc'] = (
    (RO['capx'] - RO.groupby('Name')['capx'].shift(1))
    / RO.groupby('Name')['at'].shift(1)
)
RO = RO.drop(columns=['costat', 'datafmt',"indfmt","consol","fic","gvkey","sic", "datadate","at","ebit","revt","teq","capx"])
RO = RO[RO["year"] != 2018]
bad_gvkeys = RO.loc[RO.isna().any(axis=1), 'Name'].unique()
RO = RO[~RO['Name'].isin(bad_gvkeys)]
RO_GAS_RU = eurostat[(eurostat["geo"] == "RO") & (eurostat["partner"] == "RU")]
RO_GAS_RU = RO_GAS_RU.set_index("TIME_PERIOD")
RO_GAS_TO = eurostat[(eurostat["geo"] == "RO") & (eurostat["partner"] == "TOTAL")]
RO_GAS_TO = RO_GAS_TO.set_index("TIME_PERIOD")
RO_gas = RO_GAS_RU["OBS_VALUE"]/RO_GAS_TO["OBS_VALUE"]
RO["gas"] = float(RO_gas.iloc[0])
RO["post_gas"] = RO["gas"] * RO["post"]
RO["Alternative"] = 1
# =============================================================================
# CZ
# =============================================================================
CZ = pd.read_csv("/Users/eugenmojsovic/Desktop/Teza/CapitalIQ/CZ.csv")
bad_gvkeys = CZ.loc[CZ.isna().any(axis=1), 'gvkey'].unique()
CZ = CZ[~CZ['gvkey'].isin(bad_gvkeys)]
bad_gvkeys = CZ.loc[CZ["at"] < 10, 'gvkey'].unique()
CZ = CZ[~CZ['gvkey'].isin(bad_gvkeys)]
CZ["Name"] = CZ["gvkey"]
CZ["country"] = "CZ"
CZ["ind"] = CZ["sic"].astype(str).str[:2]
CZ["ind"] = CZ["ind"].apply(map_nace_2digit)
CZ = CZ[CZ["ind"] != "Finance & insurance"]
CZ["size"] = np.log(CZ["at"])
CZ["er"] = CZ["teq"] / CZ["at"]
CZ['year'] = pd.to_datetime(CZ['datadate']).dt.year
CZ = CZ[CZ["year"] != 2025]
counts = CZ['Name'].value_counts()
valid_names = counts[counts == 7].index
CZ = CZ[CZ['Name'].isin(valid_names)]
CZ["profitability"] = CZ["ebit"] / CZ['at']
CZ["post"] = (CZ["year"] >= 2022).astype(int)
CZ2 = CZ.sort_values(["Name", "year"]).copy()
CZ2["lagged_revenue"] = CZ2.groupby("Name")["revt"].shift(1)
CZ["sales_growth"] = (
    (CZ2["revt"] - CZ2["lagged_revenue"]) / CZ2["lagged_revenue"])
CZ['cc'] = (
    (CZ['capx'] - CZ.groupby('Name')['capx'].shift(1))
    / CZ.groupby('Name')['at'].shift(1)
)
CZ = CZ.drop(columns=['costat', 'datafmt',"indfmt","consol","fic","gvkey","sic", "datadate","at","ebit","revt","teq","capx"])
CZ = CZ[CZ["year"] != 2018]
bad_gvkeys = CZ.loc[CZ.isna().any(axis=1), 'Name'].unique()
CZ = CZ[~CZ['Name'].isin(bad_gvkeys)]
CZ_GAS_RU = eurostat[(eurostat["geo"] == "CZ") & (eurostat["partner"] == "RU")]
CZ_GAS_RU = CZ_GAS_RU.set_index("TIME_PERIOD")
CZ_GAS_TO = eurostat[(eurostat["geo"] == "CZ") & (eurostat["partner"] == "TOTAL")]
CZ_GAS_TO = CZ_GAS_TO.set_index("TIME_PERIOD")
CZ_gas = CZ_GAS_RU["OBS_VALUE"]/CZ_GAS_TO["OBS_VALUE"]
CZ["gas"] = float(CZ_gas.iloc[0])
CZ["post_gas"] = CZ["gas"] * CZ["post"]
CZ["Alternative"] = 0
# =============================================================================
# SK
# =============================================================================
SK = pd.read_csv("/Users/eugenmojsovic/Desktop/Teza/CapitalIQ/SK.csv")
bad_gvkeys = SK.loc[SK.isna().any(axis=1), 'gvkey'].unique()
SK = SK[~SK['gvkey'].isin(bad_gvkeys)]
bad_gvkeys = SK.loc[SK["at"] < 10, 'gvkey'].unique()
SK = SK[~SK['gvkey'].isin(bad_gvkeys)]
SK["Name"] = SK["gvkey"]
SK["country"] = "SK"
SK["ind"] = SK["sic"].astype(str).str[:2]
SK["ind"] = SK["ind"].apply(map_nace_2digit)
SK = SK[SK["ind"] != "Finance & insurance"]
SK["size"] = np.log(SK["at"])
SK["er"] = SK["teq"] / SK["at"]
SK['year'] = pd.to_datetime(SK['datadate']).dt.year
SK = SK[SK["year"] != 2025]
counts = SK['Name'].value_counts()
valid_names = counts[counts == 7].index
SK = SK[SK['Name'].isin(valid_names)]
SK["profitability"] = SK["ebit"] / SK['at']
SK["post"] = (SK["year"] >= 2022).astype(int)
SK2 = SK.sort_values(["Name", "year"]).copy()
SK2["lagged_revenue"] = SK2.groupby("Name")["revt"].shift(1)
SK["sales_growth"] = (
    (SK2["revt"] - SK2["lagged_revenue"]) / SK2["lagged_revenue"])
SK['cc'] = (
    (SK['capx'] - SK.groupby('Name')['capx'].shift(1))
    / SK.groupby('Name')['at'].shift(1)
)
SK = SK.drop(columns=['costat', 'datafmt',"indfmt","consol","fic","gvkey","sic", "datadate","at","ebit","revt","teq","capx"])
SK = SK[SK["year"] != 2018]
bad_gvkeys = SK.loc[SK.isna().any(axis=1), 'Name'].unique()
SK = SK[~SK['Name'].isin(bad_gvkeys)]
SK_GAS_RU = eurostat[(eurostat["geo"] == "SK") & (eurostat["partner"] == "RU")]
SK_GAS_RU = SK_GAS_RU.set_index("TIME_PERIOD")
SK_GAS_TO = eurostat[(eurostat["geo"] == "SK") & (eurostat["partner"] == "TOTAL")]
SK_GAS_TO = SK_GAS_TO.set_index("TIME_PERIOD")
SK_gas = SK_GAS_RU["OBS_VALUE"]/SK_GAS_TO["OBS_VALUE"]
SK["gas"] = float(SK_gas.iloc[0])
SK["post_gas"] = SK["gas"] * SK["post"]
SK["Alternative"] = 0
# =============================================================================
# SI
# =============================================================================
SI = pd.read_csv("/Users/eugenmojsovic/Desktop/Teza/CapitalIQ/SI.csv")
bad_gvkeys = SI.loc[SI.isna().any(axis=1), 'gvkey'].unique()
SI = SI[~SI['gvkey'].isin(bad_gvkeys)]
bad_gvkeys = SI.loc[SI["at"] < 10, 'gvkey'].unique()
SI = SI[~SI['gvkey'].isin(bad_gvkeys)]
SI["Name"] = SI["gvkey"]
SI["country"] = "SI"
SI["ind"] = SI["sic"].astype(str).str[:2]
SI["ind"] = SI["ind"].apply(map_nace_2digit)
SI = SI[SI["ind"] != "Finance & insurance"]
SI["size"] = np.log(SI["at"])
SI["er"] = SI["teq"] / SI["at"]
SI['year'] = pd.to_datetime(SI['datadate']).dt.year
SI = SI[SI["year"] != 2025]
counts = SI['Name'].value_counts()
valid_names = counts[counts == 7].index
SI = SI[SI['Name'].isin(valid_names)]
SI["profitability"] = SI["ebit"] / SI['at']
SI["post"] = (SI["year"] >= 2022).astype(int)
SI2 = SI.sort_values(["Name", "year"]).copy()
SI2["lagged_revenue"] = SI2.groupby("Name")["revt"].shift(1)
SI["sales_growth"] = (
    (SI2["revt"] - SI2["lagged_revenue"]) / SI2["lagged_revenue"])
SI['cc'] = (
    (SI['capx'] - SI.groupby('Name')['capx'].shift(1))
    / SI.groupby('Name')['at'].shift(1)
)
SI = SI.drop(columns=['costat', 'datafmt',"indfmt","consol","fic","gvkey","sic", "datadate","at","ebit","revt","teq","capx"])
SI = SI[SI["year"] != 2018]
bad_gvkeys = SI.loc[SI.isna().any(axis=1), 'Name'].unique()
SI = SI[~SI['Name'].isin(bad_gvkeys)]
SI_GAS_RU = eurostat[(eurostat["geo"] == "SI") & (eurostat["partner"] == "RU")]
SI_GAS_RU = SI_GAS_RU.set_index("TIME_PERIOD")
SI_GAS_TO = eurostat[(eurostat["geo"] == "SI") & (eurostat["partner"] == "TOTAL")]
SI_GAS_TO = SI_GAS_TO.set_index("TIME_PERIOD")
SI_gas = SI_GAS_RU["OBS_VALUE"]/SI_GAS_TO["OBS_VALUE"]
SI["gas"] = float(SI_gas.iloc[0])
SI["post_gas"] = SI["gas"] * SI["post"]
SI["Alternative"] = 0
# =============================================================================
# HU
# =============================================================================
HU = pd.read_csv("/Users/eugenmojsovic/Desktop/Teza/CapitalIQ/HU.csv")
bad_gvkeys = HU.loc[HU.isna().any(axis=1), 'gvkey'].unique()
HU = HU[~HU['gvkey'].isin(bad_gvkeys)]
bad_gvkeys = HU.loc[HU["at"] < 10, 'gvkey'].unique()
HU = HU[~HU['gvkey'].isin(bad_gvkeys)]
HU["Name"] = HU["gvkey"]
HU["country"] = "HU"
HU["ind"] = HU["sic"].astype(str).str[:2]
HU["ind"] = HU["ind"].apply(map_nace_2digit)
HU = HU[HU["ind"] != "Finance & insurance"]
HU["size"] = np.log(HU["at"])
HU["er"] = HU["teq"] / HU["at"]
HU['year'] = pd.to_datetime(HU['datadate']).dt.year
HU = HU[HU["year"] != 2025]
counts = HU['Name'].value_counts()
valid_names = counts[counts == 7].index
HU = HU[HU['Name'].isin(valid_names)]
HU["profitability"] = HU["ebit"] / HU['at']
HU["post"] = (HU["year"] >= 2022).astype(int)
HU2 = HU.sort_values(["Name", "year"]).copy()
HU2["lagged_revenue"] = HU2.groupby("Name")["revt"].shift(1)
HU["sales_growth"] = (
    (HU2["revt"] - HU2["lagged_revenue"]) / HU2["lagged_revenue"])
HU['cc'] = (
    (HU['capx'] - HU.groupby('Name')['capx'].shift(1))
    / HU.groupby('Name')['at'].shift(1)
)
HU = HU.drop(columns=['costat', 'datafmt',"indfmt","consol","fic","gvkey","sic", "datadate","at","ebit","revt","teq","capx"])
HU = HU[HU["year"] != 2018]
bad_gvkeys = HU.loc[HU.isna().any(axis=1), 'Name'].unique()
HU = HU[~HU['Name'].isin(bad_gvkeys)]
HU_GAS_RU = eurostat[(eurostat["geo"] == "HU") & (eurostat["partner"] == "RU")]
HU_GAS_RU = HU_GAS_RU.set_index("TIME_PERIOD")
HU_GAS_TO = eurostat[(eurostat["geo"] == "HU") & (eurostat["partner"] == "TOTAL")]
HU_GAS_TO = HU_GAS_TO.set_index("TIME_PERIOD")
HU_gas = HU_GAS_RU["OBS_VALUE"]/HU_GAS_TO["OBS_VALUE"]
HU["gas"] = float(HU_gas.iloc[0])
HU["post_gas"] = HU["gas"] * HU["post"]
HU["Alternative"] = 0



all_datasets =  [PL, CZ, RO, SK, SI, HU]
final = pd.concat(all_datasets, ignore_index=True)
final['sales_growth'] = winsorize(final['sales_growth'], limits=[0.001, 0.001])
final['cc'] = winsorize(final['cc'], limits=[0.001, 0.001])






from linearmodels.panel import PanelOLS
data = final.set_index(['Name', 'year'])
data['alt_post_gas'] = data['post_gas'] * data['Alternative']
data["post_alt"] = data["post"] * data["Alternative"]

main_model = PanelOLS.from_formula(
    'cc ~  post_gas + size + profitability + sales_growth + er + EntityEffects + TimeEffects',
    data=data)
res = main_model.fit(
    cov_type="clustered",
    cluster_entity=True)
print(res)







