# Quantitative calculations for Environmental score (40% of ESG final industry score)
# 1. Data cleaning for each metric across all companies
# 2. Calculate metric performance per employee per year
# 3. Split into 10 quantiles and assign score (from 1 to 10) for each metric based on percentile
    # 1 - 10th percentile: 1, 11 - 20th percentile: 2, ..., 91 - 100th percentile: 10
# 4. Calculate weighted average environmental score for each company

import pandas as pd
env = pd.read_csv('Environment.csv', sep=',')
social = pd.read_csv('Social.csv', sep=',')

# Data cleaning
env.rename(columns={'EnergyConsumption(MWh)': 'Energy',
                    'GHG Emissions(tonne (Mt) of CO2e)': 'GHG',
                    'WaterUsage(tonne (Mt))' : 'Water',
                    'WasteGenerated (tonne)' : 'Waste',
                    'RenewableEnergyUse (MWh)' :'Renewable'}, inplace=True)

metric = env.columns[2:]
for col in metric:
    env[col] = env[col].astype(str)
    if env[col].str.contains(',').any():
         env[col] = env[col].str.replace(',', '')
env[metric] = env[metric].astype(float)

social['EmployeeCount'] = social['EmployeeCount'].str.replace(',', '')
pax = social[['CompanyID', 'EmployeeCount', 'ReportYear']].copy()
pax.dropna(inplace=True)
pax['EmployeeCount'] = pax['EmployeeCount'].astype(int)

# Calculate metric performance per employee
data = pd.merge(pax, env, how='inner', on=['CompanyID', 'ReportYear'])
for col in metric:
    data[col + "_per_employee"] = data[col] / data['EmployeeCount']

# Metric Score calculation        
def calc_score(perf_metric):
    perf_metric.dropna(inplace=True)
    percentiles = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    percentile_values = perf_metric.quantile([p / 100 for p in percentiles]).values
    
    def score_value(value):
        for i in range(len(percentile_values) - 1):
            if percentile_values[i] <= value < percentile_values[i + 1]:
                return 10-i
        return 1 if value == percentile_values[-1] else 10

    return perf_metric.apply(score_value)

for col in metric:
    data[col + "_score"] = calc_score(data[col + '_per_employee'])

# Score by company
total_score = data.groupby("CompanyID").agg({"Energy_score":"mean",
                                           "Water_score": "mean",
                                           "GHG_score": "mean",
                                           "Waste_score": "mean",
                                           "Renewable_score": "mean"}).reset_index()
total_score['CompanyID'] = total_score['CompanyID'].astype('category')
total_score.set_index('CompanyID', inplace=True)
print(total_score)

# Assume equal weights for each metric; NaN values not penalised
env_score_equal = total_score.mean(axis=1).reset_index(name='Environmental score')
print(env_score_equal)

# Assume different weights for each metric; NaN values will be penalised
weights = {
    'Energy_score': 0.25,
    'Water_score': 0.15,
    'GHG_score': 0.15,
    'Waste_score': 0.15,
    'Renewable_score': 0.3
}

env_score_weighted = (total_score * pd.Series(weights)).sum(axis=1)
print(env_score_weighted) 