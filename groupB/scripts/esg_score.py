import pandas as pd
import numpy as np
from decimal import Decimal
from db_connect import connect_to_db, fetch_company_info, fetch_environmental_data, fetch_social_data, fetch_governance_data, update_table

def decimal_to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return value

def calc_score(perf_metric):
    perf_metric = pd.to_numeric(perf_metric, errors='coerce')
    perf_metric.dropna(inplace=True)
    percentiles = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    percentile_values = perf_metric.quantile([p / 100 for p in percentiles]).values
    
    def score_value(value):
        for i in range(len(percentile_values) - 1):
            if percentile_values[i] <= value < percentile_values[i + 1]:
                return 10-i
        return 1 if value == percentile_values[-1] else 10

    return perf_metric.apply(score_value)

def calculate_environmental_score(env_data, pax):
    env_metric = ['EnergyConsumption', 'GHGEmissions', 'WaterUsage', 'WasteGenerated', 'RenewableEnergyUse']
    env_data = pd.merge(pax, env_data, how='inner', on=['CompanyID', 'ReportYear'])
    
    for col in env_metric:
        env_data[col] = env_data[col].apply(decimal_to_float)
        env_data['EmployeeCount'] = env_data['EmployeeCount'].apply(decimal_to_float)
        env_data[col + "_per_employee"] = env_data[col] / env_data['EmployeeCount']
        env_data[col + "_score"] = calc_score(env_data[col + '_per_employee'])
    
    env_data.fillna(0, inplace=True)
    
    env_weights = [0.25, 0.15, 0.15, 0.15, 0.3]
    env_indicator_score = env_data[[col + '_score' for col in env_metric]]
    environmental_score = (env_indicator_score * env_weights).sum(axis=1)
    
    return environmental_score

def calculate_social_score(social_data):
    binary_col = ['DataSecurity', 'CustomerPrivacy', 'Cybersecurity']
    social_data[binary_col] = social_data[binary_col].fillna(0).astype(int) * 10
    
    continuous_col = ['TrainingHours']
    for col in continuous_col:
        social_data[col + "_score"] = calc_score(social_data[col].apply(decimal_to_float))
    
    social_weights = [0.2, 0.2, 0.2, 0.2, 0.2]
    social_indicator_score = social_data[binary_col + [col + '_score' for col in continuous_col] + ['MalePercentage']]
    social_indicator_score = social_indicator_score.applymap(decimal_to_float)
    social_score = (social_indicator_score * social_weights).sum(axis=1)
    
    return social_score

def calculate_governance_score(gov_data):
    # Placeholder for governance score calculation
    # You'll need to implement this based on your governance data structure
    return pd.Series(np.random.uniform(0, 10, len(gov_data)))

def main():
    db_pool = connect_to_db()
    if not db_pool:
        print("Failed to connect to the database.")
        return
    
    # Fetch data from database
    env_data = pd.DataFrame(fetch_environmental_data(db_pool))
    social_data = pd.DataFrame(fetch_social_data(db_pool))
    gov_data = pd.DataFrame(fetch_governance_data(db_pool))
    
    # Prepare pax data
    pax = social_data[['CompanyID', 'EmployeeCount', 'ReportYear']].copy()
    pax['EmployeeCount'] = pax['EmployeeCount'].apply(decimal_to_float)
    pax.dropna(inplace=True)
    
    # Calculate scores
    environmental_score = calculate_environmental_score(env_data, pax)
    social_score = calculate_social_score(social_data)
    governance_score = calculate_governance_score(gov_data)
    
    # Combine scores into a single DataFrame
    esg_score = pd.DataFrame({
        'CompanyID': env_data['CompanyID'],
        'ReportYear': env_data['ReportYear'],
        'Environmental Score': environmental_score,
        'Social Score': social_score,
        'Governance Score': governance_score
    })

    # Fill NaN values with 0 or another appropriate value
    esg_score = esg_score.fillna(0)

    # Ensure all component scores are capped at 10
    for col in ['Environmental Score', 'Social Score', 'Governance Score']:
        esg_score[col] = esg_score[col].clip(0, 10)

    # Calculate final ESG score (out of 10)
    esg_score['Final ESG score'] = (
        esg_score['Environmental Score'] * 0.35 +
        esg_score['Social Score'] * 0.45 +
        esg_score['Governance Score'] * 0.20
    )

    # Ensure final ESG score doesn't exceed 10
    esg_score['Final ESG score'] = esg_score['Final ESG score'].clip(0, 10)

    print(esg_score)
    print(esg_score.info())
    print(esg_score['Final ESG score'])
    
    # Update the database with the new ESG scores
    update_table(db_pool, esg_score, 'esg_scores')

if __name__ == "__main__":
    main()
