
import pandas as pd
import numpy as np
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
    (eurostat["TIME_PERIOD"] >= 2018) &
    (eurostat["TIME_PERIOD"] <= 2022)]
eurostat = eurostat[eurostat["partner"].isin(["RU", "Russia", "Russian Federation", "TOTAL", "World", "WORLD"])]
eurostat = eurostat[eurostat["geo"].isin(["BG", "PL", "CZ", "HU", "SK","RO","SI"])]
BG_GAS_RU = eurostat[(eurostat["geo"] == "BG") & (eurostat["partner"] == "RU")]
BG_GAS_RU = BG_GAS_RU.set_index("TIME_PERIOD")
BG_GAS_TO = eurostat[(eurostat["geo"] == "BG") & (eurostat["partner"] == "TOTAL")]
BG_GAS_TO = BG_GAS_TO.set_index("TIME_PERIOD")
BG_l = BG_GAS_RU["OBS_VALUE"]/BG_GAS_TO["OBS_VALUE"]
BG_R = BG_l.mean()
PL_GAS_RU = eurostat[(eurostat["geo"] == "PL") & (eurostat["partner"] == "RU")]
PL_GAS_RU = PL_GAS_RU.set_index("TIME_PERIOD")
PL_GAS_TO = eurostat[(eurostat["geo"] == "PL") & (eurostat["partner"] == "TOTAL")]
PL_GAS_TO = PL_GAS_TO.set_index("TIME_PERIOD")
PL_l = PL_GAS_RU["OBS_VALUE"]/PL_GAS_TO["OBS_VALUE"]
PL_R = PL_l.mean()
CZ_GAS_RU = eurostat[(eurostat["geo"] == "CZ") & (eurostat["partner"] == "RU")]
CZ_GAS_RU = CZ_GAS_RU.set_index("TIME_PERIOD")
CZ_GAS_TO = eurostat[(eurostat["geo"] == "CZ") & (eurostat["partner"] == "TOTAL")]
CZ_GAS_TO = CZ_GAS_TO.set_index("TIME_PERIOD")
CZ_l = CZ_GAS_RU["OBS_VALUE"]/CZ_GAS_TO["OBS_VALUE"]
CZ_R = CZ_l.mean()
HU_GAS_RU = eurostat[(eurostat["geo"] == "HU") & (eurostat["partner"] == "RU")]
HU_GAS_RU = HU_GAS_RU.set_index("TIME_PERIOD")
HU_GAS_TO = eurostat[(eurostat["geo"] == "HU") & (eurostat["partner"] == "TOTAL")]
HU_GAS_TO = HU_GAS_TO.set_index("TIME_PERIOD")
HU_l = HU_GAS_RU["OBS_VALUE"]/HU_GAS_TO["OBS_VALUE"]
HU_R = HU_l.mean()
RO_GAS_RU = eurostat[(eurostat["geo"] == "RO") & (eurostat["partner"] == "RU")]
RO_GAS_RU = RO_GAS_RU.set_index("TIME_PERIOD")
RO_GAS_TO = eurostat[(eurostat["geo"] == "RO") & (eurostat["partner"] == "TOTAL")]
RO_GAS_TO = RO_GAS_TO.set_index("TIME_PERIOD")
RO_l = RO_GAS_RU["OBS_VALUE"]/RO_GAS_TO["OBS_VALUE"]
RO_R = RO_l.mean()
SK_GAS_RU = eurostat[(eurostat["geo"] == "SK") & (eurostat["partner"] == "RU")]
SK_GAS_RU = SK_GAS_RU.set_index("TIME_PERIOD")
SK_GAS_TO = eurostat[(eurostat["geo"] == "SK") & (eurostat["partner"] == "TOTAL")]
SK_GAS_TO = SK_GAS_TO.set_index("TIME_PERIOD")
SK_l = SK_GAS_RU["OBS_VALUE"]/SK_GAS_TO["OBS_VALUE"]
SK_R = SK_l.mean()
SI_GAS_RU = eurostat[(eurostat["geo"] == "SI") & (eurostat["partner"] == "RU")]
SI_GAS_RU = SI_GAS_RU.set_index("TIME_PERIOD")
SI_GAS_TO = eurostat[(eurostat["geo"] == "SI") & (eurostat["partner"] == "TOTAL")]
SI_GAS_TO = SI_GAS_TO.set_index("TIME_PERIOD")
SI_l = SI_GAS_RU["OBS_VALUE"]/SI_GAS_TO["OBS_VALUE"]
SI_R = SI_l.mean()

import matplotlib.pyplot as plt

# Store all series in dictionary
gas_series = {
    "Bulgaria": BG_l,
    "Poland": PL_l,
    "Czechia": CZ_l,
    "Hungary": HU_l,
    "Romania": RO_l,
    "Slovakia": SK_l,
    "Slovenia": SI_l
}

# Combine into dataframe
gas_df = pd.DataFrame(gas_series)

# Sort years
gas_df = gas_df.sort_index()

# Plot
plt.figure(figsize=(14, 8))

for country in gas_df.columns:
    plt.plot(
        gas_df.index,
        gas_df[country],
        marker='o',
        linewidth=2,
        label=country
    )

# Styling
plt.title("Russian Gas Import Dependence by Country (2018–2022)", fontsize=18)
plt.xlabel("Year", fontsize=14)
plt.ylabel("Russian Gas Share of Total Gas Imports", fontsize=14)

plt.legend(
    title="Country",
    loc="lower left"
)
plt.grid(True, alpha=0.3)

plt.xticks(gas_df.index, rotation=45)

plt.tight_layout()
plt.show()


























