''' *** Quantitative calculations for Environmental score (35% of ESG final industry score) ***
1. Data cleaning for each metric across all companies
2. Calculate metric performance per employee per year
3. Split into 10 quantiles and assign score (from 1 to 10) for each metric based on percentile
    1 - 10th percentile: 1, 11 - 20th percentile: 2, ..., 91 - 100th percentile: 10
4. Calculate weighted average environmental score for each company
'''
### All datasets
import pandas as pd
env = pd.read_csv('Environment.csv', sep=',')
social = pd.read_csv('Social.csv', sep=',')


# Data cleaning
env.rename(columns={'EnergyConsumption(MWh)': 'Energy',
                    'GHG Emissions(tonne (Mt) of CO2e)': 'GHG',
                    'WaterUsage(tonne (Mt))' : 'Water',
                    'WasteGenerated (tonne)' : 'Waste',
                    'RenewableEnergyUse (MWh)' :'Renewable'}, inplace=True)

env_metric = env.columns[2:]
for col in env_metric:
    env[col] = env[col].astype(str)
    if env[col].str.contains(',').any():
         env[col] = env[col].str.replace(',', '')
env[env_metric] = env[env_metric].astype(float)

social['EmployeeCount'] = social['EmployeeCount'].str.replace(',', '')
pax = social[['CompanyID', 'EmployeeCount', 'ReportYear']].copy()
pax.dropna(inplace=True)
pax['EmployeeCount'] = pax['EmployeeCount'].astype(int)


# Calculate metric performance per employee
env_data = pd.merge(pax, env, how='inner', on=['CompanyID', 'ReportYear'])
for col in env_metric:
    env_data[col + "_per_employee"] = env_data[col] / env_data['EmployeeCount']

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

# Env score calculation
for col in env_metric:
    env_data[col + "_score"] = calc_score(env_data[col + '_per_employee'])
env_data.fillna(0, inplace=True)
yearly_env_data = env_data.groupby('ReportYear').value_counts().reset_index()
yearly_env_data.drop(columns='count', inplace=True)

# Penalise metric if not reported
env_weights = [0.25, 0.15, 0.15, 0.15, 0.3]
final_env_score = yearly_env_data[['ReportYear', 'CompanyID', 'Energy_score', 'Water_score', 'GHG_score', 'Waste_score', 'Renewable_score']].copy()
env_indicator_score = final_env_score[['Energy_score', 'Water_score', 'GHG_score', 'Waste_score', 'Renewable_score']]
environmental_score = (env_indicator_score * env_weights).sum(axis=1)
final_env_score['Average Environmental Score'] = environmental_score
final_env_score[["Water_score", "Waste_score", "Renewable_score"]] = final_env_score[["Water_score", "Waste_score", "Renewable_score"]].astype(int)
final_env_score.sort_values(by=['CompanyID', 'ReportYear'], inplace = True)
print(final_env_score)


''' *** Quantitative calculations for Social score (45% of ESG final industry score) ***
1. Split into 2 different categories: 
    - Discrete metrics (binary 1, score 10: disclosure; binary 0, score 0: no disclosure)
    Define set of key words to search for:
    a) Data security
        - Data security
        - Data protection 
    b) Customer privacy
        - Privacy protection
        - Consumer protection
        - Customer protection
    c) Cybersecurity
        - Malware 
        - Phishing
        - Network security
        - Information security
        - Cybersecurity
        - Cyberattack
        
    d) Gender diversity metrics
    e) Age-based diversity metrics 
        # both (d) and (e) have statistics reported under diversity and inclusion table: 1, else 0
        
    - Continuous metrics (work-related fatalities, training hours) -> same quantitative scoring system as Env
    
2. Calculate weighted average social score for each company
    - Each metric is then converted to a score from 1 to 10 based on percentile (continuous),
        or a score of 0 or 10 for disclosure (discrete)
'''

# sample data format for social.csv imported above
social_data = pd.DataFrame({
    'CompanyID': [1,2,2,3,4,4,5,6],
    'ReportYear': [2023,2022,2023,2023,2022,2023,2022,2023],
    "Keyword: Data security": [1,1,1,1,0,0,0,0],
    "Keyword: Customer privacy": [1,1,0,0,1,1,0,0],
    "Keyword: Cybersecurity": [1,0,1,0,1,0,1,0],
    "Gender diversity metric": [0,1,0,1,0,1,0,1],
    "Age-based diversity metric": [0,0,1,1,0,1,1,0], # binary -> 0: no disclosure, 1: disclosure
    "Work-related Fatalies/ Injuries recorded (%)": [10,2,3,0.4,3.8,1,20,13], # see if want to split into sub metrics
    "Development and training (training hours)": [100,200,300,400,500,600,700,800]
})

binary_col = social_data.columns[2:7]
social_data[binary_col] = social_data[binary_col] * 10 # score of 10 for disclosure, 0 for no disclosure
continuous_col = social_data.columns[7:].to_list() # continuous metrics
social_data.fillna(0, inplace=True)

# Assign scores for continuous metrics
for col in continuous_col:
    social_data[col + "_score"] = calc_score(social_data[col])

# Weighted average social score
social_weights = [0.2,0.2,0.2,0.1,0.1,0.1,0.1]
yearly_social_data = social_data.groupby(['ReportYear'])[['CompanyID', 'Work-related Fatalies/ Injuries recorded (%)_score', 
                                                         "Development and training (training hours)_score"]].value_counts().reset_index()
yearly_social_data.drop(columns='count', inplace=True)
social_data.merge(yearly_social_data, on=['CompanyID', 'ReportYear'], how='left')

social_indicator_score = social_data[['Keyword: Data security', 'Keyword: Customer privacy', 'Keyword: Cybersecurity',
              "Gender diversity metric", "Age-based diversity metric", 
              'Work-related Fatalies/ Injuries recorded (%)_score', 
              "Development and training (training hours)_score"]]
final_social_score = (social_indicator_score * social_weights).sum(axis=1)
social_data['Average Social Score'] = final_social_score
social_data.drop(columns = ['Work-related Fatalies/ Injuries recorded (%)', 
                            "Development and training (training hours)"], inplace=True)
social_data.sort_values(by=['CompanyID', 'ReportYear'])
print(social_data)


''' *** Quantitative calculations for Governance score (20% of ESG final industry score) ***
1. Discrete metrics (binary 0/1, score of 0 or 10 for disclosure)
    Define set of key words to search for:
    a) Ethical behaviour (30%)
        - Ethics
        - Compliance
        - Anti-corruption
        - Anti-bribery
        - Transparency
    b) Board composition (15%)
        - Board committee
        - Board composition
        - Board independence
    c) Risk management (30%)
        - Risk management
        - Risk oversight
        - Risk assessment
    d) Certifications List (5% each, 25% total)
        - ISO 14001
        - ISO 50001
        - ISO 45001
        - ISO 14064
        - Carbon trust
2. Calculate weighted average governance score for each company
'''

# sample data format for governance.csv (to be imported above)
gov_data = pd.DataFrame({
    'CompanyID': [1,2,2,3,4,4,5,6],
    'ReportYear': [2023,2022,2023,2023,2022,2023,2022,2023],
    "Keyword: Ethical behaviour": [1,1,1,1,0,0,0,0],
    "Keyword: Board Composition": [1,1,0,0,1,1,0,0],
    "Keyword: Risk management": [1,0,1,0,1,0,1,0],
    "Certification list": [0,1,4,1,5,2,3,3] # Score 10/10: all certifications awarded, : none awarded
})

gov_col = gov_data.columns[2:]
gov_keyword = gov_data.columns[2:5]
certificate = gov_data.columns[5]
gov_data.fillna(0, inplace=True)
gov_data[gov_keyword] = gov_data[gov_keyword] * 10 # scores for main keywords
gov_data[certificate] = gov_data[certificate] * 2 # scores for certifications

# Weighted average governance score
gov_weights = [0.3, 0.15, 0.3, 0.25]
gov_indicator_score = gov_data.iloc[:,2:]
final_gov_score = (gov_indicator_score * gov_weights).sum(axis=1)
gov_data['Average Governance Score'] = final_gov_score
gov_data.sort_values(by=['CompanyID', 'ReportYear'])
print(gov_data)

### Final ESG score calculation
# esg_score = pd.concat([gov_data, social_data, final_env_score], axis=1)
# esg_score['Final ESG score'] = (esg_score['Average Governance Score'] * 0.2 
#                                 + esg_score['Average Social Score'] * 0.45
#                                 + esg_score['Average Environmental Score'] * 0.35))
# print(esg_score)