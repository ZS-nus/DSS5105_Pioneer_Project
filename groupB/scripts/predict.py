import pandas as pd
import numpy as np
from decimal import Decimal
from db_connect import connect_to_db, fetch_ESG_data
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import matplotlib.pyplot as plt

db_pool = connect_to_db()
if not db_pool:
    print("Failed to connect to the database.")
    exit()
else:
    esg_score = fetch_ESG_data(db_pool)

esg_ts_data = pd.DataFrame(esg_score)
esg_ts_data = esg_ts_data[['CompanyID', 'ReportYear', 'Environmental_Score', 'Social_Score', 'Governance_Score', 'Final_ESG_score']].copy()

esg_ts_data.reset_index(drop=True, inplace=True)

esg_ts_data.fillna(esg_ts_data.mean(), inplace=True)

# Set the number of years to forecast
forecast_years = 5
company_forecasts = []

# Forcast for each company
for company_id, group in esg_ts_data.groupby('CompanyID'):
    
    # Ensure data is sorted by year and set year as index
    group = group.sort_values(by='ReportYear').set_index('ReportYear')

    if len(group) < 2:
        # If less than 2 years of data, use the mean to forecast the future
        env_forecast = [group['Environmental_Score'].mean()] * forecast_years
        soc_forecast = [group['Social_Score'].mean()] * forecast_years
        gov_forecast = [group['Governance_Score'].mean()] * forecast_years
    else:
        # Use exponential smoothing for time series forecasting
        env_model = ExponentialSmoothing(group['Environmental_Score'], trend="add", seasonal=None, initialization_method="estimated")
        soc_model = ExponentialSmoothing(group['Social_Score'], trend="add", seasonal=None, initialization_method="estimated")
        gov_model = ExponentialSmoothing(group['Governance_Score'], trend="add", seasonal=None, initialization_method="estimated")

        env_fit = env_model.fit()
        soc_fit = soc_model.fit()
        gov_fit = gov_model.fit()

        # Forecast
        env_forecast = env_fit.forecast(steps=forecast_years)
        soc_forecast = soc_fit.forecast(steps=forecast_years)
        gov_forecast = gov_fit.forecast(steps=forecast_years)

    # Combine forecasts using weighted average
    final_forecast = (0.35 * np.array(env_forecast) + 
                      0.45 * np.array(soc_forecast) + 
                      0.2 * np.array(gov_forecast))
    
    # Clip values to be between 0 and 10
    env_forecast = np.clip(env_forecast, 0, 10)
    soc_forecast = np.clip(soc_forecast, 0, 10)
    gov_forecast = np.clip(gov_forecast, 0, 10)
    final_forecast = np.clip(final_forecast, 0, 10)

    # Years
    last_year = group.index[-1]
    future_years = [last_year + i for i in range(1, forecast_years + 1)]

    forecast_df = pd.DataFrame({
        'CompanyID': company_id, 
        'Year': future_years, 
        'Environmental_Forecast': env_forecast, 
        'Social_Forecast': soc_forecast, 
        'Governance_Forecast': gov_forecast, 
        'Predicted ESG Score': final_forecast
    })
    company_forecasts.append(forecast_df)

final_forecast_df = pd.concat(company_forecasts, ignore_index=True)

print(final_forecast_df[[ 'Environmental_Forecast', 'Governance_Forecast', 'Predicted ESG Score']])

# print(final_forecast_df.info())



