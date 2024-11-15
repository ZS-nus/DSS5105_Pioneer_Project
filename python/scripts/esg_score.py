import sys
import os
from pathlib import Path

# Get the absolute path to the script's directory
script_dir = Path(__file__).parent.absolute()

# Add both the script's directory and its parent to the Python path
sys.path.append(str(script_dir))  # For db_connect.py
sys.path.append(str(script_dir.parent))  # For config.py

from db_connect import get_connection_pool, fetch_company_info, fetch_environmental_data, fetch_social_data, fetch_governance_data, update_table
import pandas as pd
import numpy as np
from decimal import Decimal

# Define ESG weights
ESG_WEIGHTS = {
    'Environmental': 0.4,
    'Social': 0.3,
    'Governance': 0.3
}

# Add a function to update weights
def update_esg_weights(env_weight: float, social_weight: float, gov_weight: float):
    """Update ESG weights ensuring they sum to 1"""
    total = env_weight + social_weight + gov_weight
    if abs(total - 1.0) > 0.0001:  # Allow small floating point differences
        raise ValueError("ESG weights must sum to 1.0")
        
    ESG_WEIGHTS['Environmental'] = float(env_weight)
    ESG_WEIGHTS['Social'] = float(social_weight)
    ESG_WEIGHTS['Governance'] = float(gov_weight)

def decimal_to_float(value):
    """Convert decimal or any numeric type to float"""
    if isinstance(value, Decimal):
        return float(value)
    elif pd.isna(value):
        return 0.0
    return float(value)

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
    env_metric = ['EnergyConsumption', 'GHGEmissions', 'WaterUsage', 'WasteGenerated']
    env_data = pd.merge(pax, env_data, how='inner', on=['CompanyID', 'ReportYear'])
    
    # Convert EmployeeCount to float first
    env_data['EmployeeCount'] = env_data['EmployeeCount'].apply(decimal_to_float)
    env_data['EmployeeCount'].fillna(env_data['EmployeeCount'].mean(), inplace=True)
    
    for col in env_metric:
        # Convert column to float first
        env_data[col] = env_data[col].apply(decimal_to_float)
        
        # Fill missing values with 25th percentile
        percentile_25 = env_data[col].quantile(0.25)
        env_data[col].fillna(percentile_25, inplace=True)
        
        env_data[col + "_per_employee"] = env_data[col] / env_data['EmployeeCount']
        env_data[col + "_score"] = calc_score(env_data[col + '_per_employee'])
        # Convert score to float
        env_data[col + "_score"] = env_data[col + "_score"].apply(decimal_to_float)
    
    env_weights = [0.4, 0.2, 0.2, 0.2]
    env_indicator_score = env_data[[col + '_score' for col in env_metric]]
    
    # Ensure all values are float
    environmental_score = pd.Series(0.0, index=env_indicator_score.index)
    for col, weight in zip(env_indicator_score.columns, env_weights):
        environmental_score += env_indicator_score[col].apply(decimal_to_float) * weight
    
    # Round to 3 decimal places
    environmental_score = environmental_score.round(3)
    
    # Calculate percentile rank within each year and scale to 10
    env_data['Percentile_rank'] = environmental_score.groupby(env_data['ReportYear']).rank(pct=True) * 10
    
    # Clip the final percentile rank
    env_data['Percentile_rank'] = env_data['Percentile_rank'].clip(0, 10)
    
    # Individual env scores
    env_score = env_data[['CompanyID', 'ReportYear', 'EnergyConsumption_score', 'GHGEmissions_score', 
                          'WaterUsage_score', 'WasteGenerated_score']].copy()

    # Return the percentile rank as the final environmental score
    return env_data['Percentile_rank'], env_score


def calculate_social_score(social_data):
    binary_col = ['DataSecurity', 'CustomerPrivacy', 'Cybersecurity', 'GenderStats', 'AgeStats']
    
    # Convert binary columns to float
    for col in binary_col:
        social_data[col] = social_data[col].apply(decimal_to_float)
    social_data[binary_col] = social_data[binary_col].fillna(0) * 10
    
    # Convert and calculate injury score
    social_data['WorkRelatedInjuries'] = social_data['WorkRelatedInjuries'].apply(decimal_to_float)
    social_data['WorkRelatedInjuries_score'] = calc_score(social_data['WorkRelatedInjuries'])
    
    # Convert and calculate training score
    social_data['TrainingHours'] = social_data['TrainingHours'].apply(decimal_to_float)
    social_data['TrainingHours_score'] = train_score(social_data['TrainingHours'])
    
    social_weights = [0.2, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1]
    social_indicator_score = social_data[binary_col + ['WorkRelatedInjuries_score', 'TrainingHours_score']]
    
    # Calculate weighted sum ensuring float values
    social_score = pd.Series(0.0, index=social_indicator_score.index)
    for col, weight in zip(social_indicator_score.columns, social_weights):
        social_score += social_indicator_score[col].apply(decimal_to_float) * weight
    
    # Clip to ensure scores are within range
    social_score = social_score.clip(0, 10)
    
    return social_score

def calculate_governance_score(gov_data):
    binary_col = ['BoardComposition', 'EthicalBehaviour', 'RiskManagement']
    certificate = ['CertificationList']
    
    # Convert all columns to float first
    for col in binary_col + certificate:
        gov_data[col] = gov_data[col].apply(decimal_to_float)
    
    gov_data.fillna(0, inplace=True)
    
    # Handle binary columns normally
    gov_data[binary_col] = gov_data[binary_col] * 10
    
    # Calculate certification score using percentile ranking
    cert_scores = pd.Series(0.0, index=gov_data.index)
    if not gov_data[certificate[0]].empty:
        # Use percentile ranking for certificates
        cert_scores = gov_data[certificate[0]].rank(pct=True) * 10
    
    # Combine scores with weights
    gov_weights = [0.15, 0.3, 0.3, 0.25]
    binary_scores = gov_data[binary_col]
    
    gov_score = pd.Series(0.0, index=gov_data.index)
    
    # Apply weights to binary columns
    for col, weight in zip(binary_col, gov_weights[:-1]):
        gov_score += binary_scores[col].apply(decimal_to_float) * weight
    
    # Add weighted certification score
    gov_score += cert_scores * gov_weights[-1]
    
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
    
    # Debug: Print the shapes of our dataframes
    print(f"Environmental data shape: {env_data.shape}")
    print(f"Social data shape: {social_data.shape}")
    print(f"Governance data shape: {gov_data.shape}")
    
    # Prepare pax data
    pax = social_data[['CompanyID', 'EmployeeCount', 'ReportYear']].copy()
    pax['EmployeeCount'] = pax['EmployeeCount'].apply(decimal_to_float)
    pax.dropna(inplace=True)
    
    # Calculate scores
    environmental_score = calculate_environmental_score(env_data, pax)
    social_score = calculate_social_score(social_data)
    governance_score = calculate_governance_score(gov_data)
    
    # Debug: Print sample of scores
    print("\nSample of calculated scores:")
    print("Environmental scores:", environmental_score.head())
    print("Social scores:", social_score.head())
    print("Governance scores:", governance_score.head())
    
    # Combine scores into a single DataFrame for ESG scores
    esg_score = pd.DataFrame({
        'CompanyID': env_data['CompanyID'],
        'ReportYear': env_data['ReportYear'],
        'Environmental_Score': environmental_score,
        'Social_Score': social_score,
        'Governance_Score': governance_score
    })

    # Fill NaN values and process ESG scores
    esg_score = esg_score.fillna(0)
    for col in ['Environmental_Score', 'Social_Score', 'Governance_Score']:
        esg_score[col] = esg_score[col].clip(0, 10)
    
    # Debug: Print before final calculation
    print("\nBefore final ESG calculation:")
    print(esg_score.head())
    
    # Calculate final ESG score with weights
    esg_score['Final_ESG_score'] = (
        esg_score['Environmental_Score'] * ESG_WEIGHTS['Environmental'] +
        esg_score['Social_Score'] * ESG_WEIGHTS['Social'] +
        esg_score['Governance_Score'] * ESG_WEIGHTS['Governance']
    )
    esg_score['Final_ESG_score'] = esg_score['Final_ESG_score'].clip(0, 10)
    
    # Debug: Print after final calculation
    print("\nAfter final ESG calculation:")
    print(esg_score.head())
    
    # Update the env_score table (individual env components)
    env_score = calculate_environmental_score(env_data, pax)[1]
    update_table(db_pool, env_score, 'env_score')
    
    # Update the ESG scores table
    print("\nUpdating database...")
    update_table(db_pool, esg_score, 'esg_scores')
    print("Database update complete")


    
if __name__ == "__main__":
    main()
