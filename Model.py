import pandas as pd
from linearmodels.panel import PanelOLS
data = pd.read_csv("/Users/eugenmojsovic/Desktop/Teza/clean2.csv")
data = data.set_index(['Name', 'year'])
data['alt_post_gas'] = data['post_gas'] * data['Alternative']
data["post_alt"] = data["post"] * data["Alternative"]
data["alt_gas"] = data["Alternative"] * data["gas"]

main_model = PanelOLS.from_formula(
    'investment_proxy ~  post_gas + Size + profitability + sales_g + er + EntityEffects + TimeEffects',
    data=data)
res = main_model.fit(
    cov_type="clustered",
    cluster_entity=True)
print(res)

model2 = PanelOLS.from_formula(
    'investment_proxy ~ alt_post_gas + post_gas  + post_alt + Size + profitability + sales_g + er  + EntityEffects + TimeEffects',
    data=data)
res2 = model2.fit(
    cov_type="clustered",
    cluster_entity=True)
print(res2)

# =============================================================================
# Industry specific
# =============================================================================

hiEXP = data[data["ind"].isin(["Manufacturing","Utilities","Transport","Construction"])]
model_hiEXP = PanelOLS.from_formula(
    'investment_proxy ~  post_gas + Size + profitability + sales_g + er + EntityEffects + TimeEffects',
    data=hiEXP)
res_hiEXP = model_hiEXP.fit(
    cov_type="clustered",
    cluster_entity=True)
print(res_hiEXP)

midEXP = data[data["ind"].isin(["Trade","Real estate","Accommodation & food"])]
model_midEXP = PanelOLS.from_formula(
    'investment_proxy ~  post_gas + Size + profitability + sales_g + er + EntityEffects + TimeEffects',
    data=midEXP)
res_midEXP = model_midEXP.fit(
    cov_type="clustered",
    cluster_entity=True)
print(res_midEXP)

lowEXP = data[data["ind"].isin(["ICT","Public & social services","Professional services","Other"])]
model_lowEXP = PanelOLS.from_formula(
    'investment_proxy ~  post_gas + Size + profitability + sales_g + er + EntityEffects + TimeEffects',
    data=lowEXP)
res_lowEXP = model_lowEXP.fit(
    cov_type="clustered",
    cluster_entity=True)
print(res_lowEXP)

import matplotlib.pyplot as plt

hi_avg = hiEXP.groupby("year")["investment_proxy"].mean()
mid_avg = midEXP.groupby("year")["investment_proxy"].mean()
low_avg = lowEXP.groupby("year")["investment_proxy"].mean()

plt.figure(figsize=(10, 6))

plt.plot(hi_avg.index, hi_avg.values, marker="o",
         label="High Direct Energy Exposure")
plt.plot(mid_avg.index, mid_avg.values, marker="o",
         label="Moderate/Indirect Energy Exposure")
plt.plot(low_avg.index, low_avg.values, marker="o",
         label="Low Direct Energy Exposure")

plt.xlabel("Year")
plt.ylabel("Average Investment Proxy")
plt.title("Average Investment Proxy Over Time by Energy Exposure Group")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# =============================================================================
# Robustness check1 - post is 23 and 24 instead of 22 23 24
# =============================================================================

dataR = data.copy()
dataR.loc[dataR.index == 2022, 'post'] = 0
modelR = PanelOLS.from_formula(
    'investment_proxy ~  post_gas + Size + profitability + sales_g + er + EntityEffects + TimeEffects',
    data=dataR)
resR = modelR.fit(
    cov_type="clustered",
    cluster_entity=True)
print(resR)

# =============================================================================
# Robustness check2 dataset with croatia
# =============================================================================
dataR2 =  pd.read_csv("/Users/eugenmojsovic/Desktop/Teza/wcro.csv")
dataR2 = dataR2.set_index(['Name', 'year'])

modelR2 = PanelOLS.from_formula(
    'investment_proxy ~  post_gas + Size + profitability + sales_g + er + EntityEffects + TimeEffects',
    data=dataR2)
resR2 = modelR2.fit(
    cov_type="clustered",
    cluster_entity=True)
print(resR2)
















