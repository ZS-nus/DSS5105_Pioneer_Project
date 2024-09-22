import pandas as pd
from db_connect import connect_to_db, fetch_company_info, fetch_environmental_data, fetch_social_data, update_table
import numpy as np

# Connect to the database
db_pool = connect_to_db()

if db_pool:
    # Fetch company info
    company_info_data = fetch_company_info(db_pool)
    company_info_df = pd.DataFrame(company_info_data)

    # Fetch environmental data
    environmental_data = fetch_environmental_data(db_pool)
    environmental_df = pd.DataFrame(environmental_data)

    # Fetch social data
    social_data = fetch_social_data(db_pool)
    social_df = pd.DataFrame(social_data)
    

    # Data cleaning for environmental data
    env = environmental_df
    env.rename(columns={'EnergyConsumption': 'Energy',
                        'GHGEmissions': 'GHG',
                        'WaterUsage': 'Water',
                        'WasteGenerated': 'Waste',
                        'RenewableEnergyUse': 'Renewable'}, inplace=True)

    metric = ['Energy', 'GHG', 'Water', 'Waste', 'Renewable']
    for col in metric:
        env[col] = env[col].astype(str)
        env[col] = env[col].replace('None', '0')  # Replace 'None' with '0'
        if env[col].str.contains(',').any():
            env[col] = env[col].str.replace(',', '')
    env[metric] = env[metric].astype(float)

    # Data cleaning for social data
    social = social_df
    social['EmployeeCount'] = social['EmployeeCount'].astype(str).str.replace(',', '')
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

    # Score by company and year
    total_score = data.groupby(["CompanyID", "ReportYear"]).agg({
        "Energy_score": "mean",
        "Water_score": "mean",
        "GHG_score": "mean",
        "Waste_score": "mean",
        "Renewable_score": "mean"
    }).reset_index()

    # Assume different weights for each metric
    weights = {
        'Energy_score': 0.25,
        'Water_score': 0.15,
        'GHG_score': 0.15,
        'Waste_score': 0.15,
        'Renewable_score': 0.3
    }

    # Calculate weighted score
    for metric, weight in weights.items():
        total_score[f'{metric}_weighted'] = total_score[metric] * weight

    # Calculate final weighted score
    total_score['env_score_weighted'] = total_score[[f'{metric}_weighted' for metric in weights.keys()]].sum(axis=1)

    print("Environmental Score (Weighted) by Company and Year:")
    print(total_score[['CompanyID', 'ReportYear', 'env_score_weighted']].head(5))
    
    # Update the e_score table in the database
    update_table(db_pool, total_score, 'e_score')


else:
    print("Failed to connect to the database. Please check your connection settings.")
