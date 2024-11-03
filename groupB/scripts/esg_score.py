import pandas as pd
import numpy as np
from decimal import Decimal
from db_connect import get_connection_pool, fetch_environmental_data, fetch_social_data, fetch_governance_data, update_table

def decimal_to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return value

def calc_score(perf_metric):
    perf_metric = pd.to_numeric(perf_metric, errors='coerce')
    perf_metric.dropna(inplace=True)
    standardised_perf_metric = (perf_metric - perf_metric.mean()) / perf_metric.std()
    percentiles = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    percentile_values = standardised_perf_metric.quantile([p / 100 for p in percentiles]).values
    
    def score_value(value):
        for i in range(len(percentile_values) - 1):
            if percentile_values[i] <= value < percentile_values[i + 1]:
                return 10-i
        return 1 if value == percentile_values[-1] else 10

    return standardised_perf_metric.apply(score_value)

def train_score(TrainingHours): # specifically for training hours -> higher is better
    TrainingHours = pd.to_numeric(TrainingHours, errors='coerce')
    TrainingHours.dropna(inplace=True)
    standardised_train = (TrainingHours - TrainingHours.mean()) / TrainingHours.std()

    percentiles = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    percentile_values = standardised_train.quantile([p / 100 for p in percentiles]).values
    
    def score_value(value):
        for i in range(len(percentile_values) - 1):
            if percentile_values[i] <= value < percentile_values[i + 1]:
                return i+1
        return 10 if value == percentile_values[-1] else 1

    return standardised_train.apply(score_value)


def calculate_environmental_score(env_data, pax):
    env_metric = ['EnergyConsumption', 'GHGEmissions', 'WaterUsage', 'WasteGenerated'] # renewable removed
    env_data = pd.merge(pax, env_data, how='inner', on=['CompanyID', 'ReportYear'])
    
    for col in env_metric:
        env_data[col] = env_data[col].apply(decimal_to_float)
        env_data['EmployeeCount'] = env_data['EmployeeCount'].apply(decimal_to_float)
        env_data[col + "_per_employee"] = env_data[col] / env_data['EmployeeCount']
        env_data[col + "_score"] = calc_score(env_data[col + '_per_employee'])
    
    env_data.fillna(0, inplace=True)
    
    env_weights = [0.4, 0.2, 0.2, 0.2]
    env_indicator_score = env_data[[col + '_score' for col in env_metric]]
    environmental_score = (env_indicator_score * env_weights).sum(axis=1)
    
    return environmental_score

def calculate_social_score(social_data):
    binary_col = ['DataSecurity', 'CustomerPrivacy', 'Cybersecurity', 'GenderStats', 'AgeStats']
    social_data[binary_col] = social_data[binary_col].fillna(0).astype(int) * 10
    
    social_data['WorkRelatedInjuries' + "_score"] = calc_score(social_data['WorkRelatedInjuries'].apply(decimal_to_float))
    social_data['TrainingHours' + "_score"] = train_score(social_data['TrainingHours']).apply(decimal_to_float)
    
    social_weights = [0.2, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1]
    social_indicator_score = social_data[binary_col + ['WorkRelatedInjuries' + "_score"] + ['TrainingHours' + "_score"]]
    social_indicator_score = social_indicator_score.applymap(decimal_to_float)
    social_score = (social_indicator_score * social_weights).sum(axis=1)
    
    return social_score

def calculate_governance_score(gov_data):
    binary_col = ['BoardComposition', 'EthicalBehaviour', 'RiskManagement']
    certificate = ['CertificationList']
    gov_data.fillna(0, inplace=True)
    gov_data[binary_col] = gov_data[binary_col] * 10 # scores for main keywords
    gov_data[certificate] = gov_data[certificate] * 2 # scores for certifications
    
    gov_weights = [0.15, 0.3, 0.3, 0.25]
    gov_indicator_score = gov_data[binary_col + certificate].applymap(decimal_to_float)
    gov_score = (gov_indicator_score * gov_weights).sum(axis=1)
    
    return gov_score


def main():
    db_pool = get_connection_pool()
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
    # Create environmental score DataFrame
    e_score_df = pd.DataFrame({
        'CompanyID': env_data['CompanyID'],
        'ReportYear': env_data['ReportYear'],
        'Environmental_Score': environmental_score
    })
    
    # Fill NaN values and ensure scores are capped at 10
    e_score_df = e_score_df.fillna(0)
    e_score_df['Environmental_Score'] = e_score_df['Environmental_Score'].clip(0, 10)
    
    
    # Calculate and update other scores as before...
    social_score = calculate_social_score(social_data)
    governance_score = calculate_governance_score(gov_data)
    
    # Combine scores into a single DataFrame for ESG scores
    esg_score = pd.DataFrame({
        'CompanyID': env_data['CompanyID'],
        'ReportYear': env_data['ReportYear'],
        'Environmental_Score': environmental_score,
        'Social_Score': social_score,
        'Governance_Score': governance_score
    })

    # Fill NaN values and process ESG scores as before...
    esg_score = esg_score.fillna(0)
    for col in ['Environmental_Score', 'Social_Score', 'Governance_Score']:
        esg_score[col] = esg_score[col].clip(0, 10)

    esg_score['Final_ESG_score'] = (
        esg_score['Environmental_Score'] * 0.4 +
        esg_score['Social_Score'] * 0.3 +
        esg_score['Governance_Score'] * 0.3
    )
    esg_score['Final_ESG_score'] = esg_score['Final_ESG_score'].clip(0, 10)
    
    # Update the ESG scores table
    update_table(db_pool, esg_score, 'esg_scores')

if __name__ == "__main__":
    main()
