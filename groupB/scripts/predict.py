import pandas as pd
import numpy as np
from decimal import Decimal
from db_connect import connect_to_db, fetch_ESG_data, update_predict_table
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning, message="divide by zero encountered in log")
warnings.filterwarnings("ignore", category=RuntimeWarning, message="invalid value encountered in scalar add")
warnings.filterwarnings("ignore", category=RuntimeWarning, message="divide by zero encountered in log")

db_pool = connect_to_db()
if not db_pool:
    print("Failed to connect to the database.")
    exit()
else:
    esg_score = fetch_ESG_data(db_pool)

esg_ts_data = pd.DataFrame(esg_score)
esg_ts_data = esg_ts_data[['CompanyID', 'ReportYear', 'Environmental_Score', 'Social_Score', 'Governance_Score', 'Final_ESG_score']].copy()

# Convert ReportYear to datetime
esg_ts_data['ReportYear'] = pd.to_datetime(esg_ts_data['ReportYear'], format='%Y')

esg_ts_data.reset_index(drop=True, inplace=True)

esg_ts_data.fillna(esg_ts_data.mean(), inplace=True)

# Set the number of years to forecast
forecast_years = 3
company_data = []

# Process data for each company
for company_id, group in esg_ts_data.groupby('CompanyID'):
    
    # Ensure data is sorted by year and set year as index
    group = group.sort_values(by='ReportYear').set_index('ReportYear')

    # Add actual data to the company_data list
    actual_df = group.reset_index().rename(columns={
        'ReportYear': 'Year',
        'Environmental_Score': 'Environmental',
        'Social_Score': 'Social',
        'Governance_Score': 'Governance',
        'Final_ESG_score': 'ESG_Score'
    })
    actual_df['Data_Type'] = 'Actual'
    actual_df['Year'] = actual_df['Year'].dt.year
    company_data.append(actual_df)

    if len(group) < 2:
        # If less than 2 years of data, use the mean to forecast the future
        last_year = group.index[-1].year
        future_years = pd.date_range(start=f"{last_year+1}-01-01", periods=forecast_years, freq='YS')
        forecast_df = pd.DataFrame({
            'CompanyID': company_id,
            'Year': future_years.year,
            'Environmental': [group['Environmental_Score'].mean()] * forecast_years,
            'Social': [group['Social_Score'].mean()] * forecast_years,
            'Governance': [group['Governance_Score'].mean()] * forecast_years
        })
    else:
        # Use exponential smoothing for time series forecasting
        models = {
            'Environmental': ExponentialSmoothing(group['Environmental_Score'], trend="add", seasonal=None),
            'Social': ExponentialSmoothing(group['Social_Score'], trend="add", seasonal=None),
            'Governance': ExponentialSmoothing(group['Governance_Score'], trend="add", seasonal=None)
        }
        
        fits = {k: v.fit() for k, v in models.items()}
        
        # Forecast
        forecasts = {k: v.forecast(steps=forecast_years) for k, v in fits.items()}
        
        # Create forecast DataFrame
        last_year = group.index[-1].year
        future_years = pd.date_range(start=f"{last_year+1}-01-01", periods=forecast_years, freq='YS')
        forecast_df = pd.DataFrame({
            'CompanyID': company_id,
            'Year': future_years.year,
            'Environmental': forecasts['Environmental'],
            'Social': forecasts['Social'],
            'Governance': forecasts['Governance']
        })

    # Calculate final ESG score
    forecast_df['ESG_Score'] = (
        0.35 * forecast_df['Environmental'] + 
        0.45 * forecast_df['Social'] + 
        0.2 * forecast_df['Governance']
    )
    
    # Clip values to be between 0 and 10
    for col in ['Environmental', 'Social', 'Governance', 'ESG_Score']:
        forecast_df[col] = np.clip(forecast_df[col], 0, 10)

    forecast_df['Data_Type'] = 'Predicted'
    company_data.append(forecast_df)

final_df = pd.concat(company_data, ignore_index=True)

# Sort the DataFrame by CompanyID and Year
final_df = final_df.sort_values(['CompanyID', 'Year'])

# print(final_df.info())
print(final_df[['CompanyID', 'Year', 'Environmental', 'Social', 'Governance', 'ESG_Score', 'Data_Type']].head(10))

if db_pool:
    # Update the predictions table
    update_predict_table(db_pool, final_df)
else:
    print("Failed to connect to the database. Predictions were not saved.")
