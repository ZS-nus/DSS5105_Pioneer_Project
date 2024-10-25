import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from db_connect import connect_to_db, fetch_ESG_financial_data


def main():
    db_pool = connect_to_db()
    if not db_pool:
        print("Failed to connect to the database.")
        return
    
    
    ## Sample dataset for ESG vs financial performance
    # Unique company and market identifiers from yahoo finance 
    companies = {
        4: 'IBM',
        6: '005930.KS',
        2: '0992.HK',
        5: 'META',
        3: '1810.HK',
        7: 'GOOGL',
        8: '0700.HK',
        1: 'AAPL'
    }
    df = pd.DataFrame(companies.items(), columns=['CompanyID', 'Company Ticker'])
    df['Market Ticker'] = [
        '^GSPC',  # IBM
        '^KS11',  # Samsung
        '^HSI',   # Lenovo
        '^GSPC',  # Meta
        '^HSI',   # Xiaomi
        '^GSPC',  # Google
        '^HSI',   # Tencent
        '^GSPC'   # Apple
    ]

    # Year 2023
    start_date = '2023-01-01'
    end_date = '2024-01-01'

    beta_results = pd.DataFrame(columns=['CompanyID', 'Beta'])

    # Calculate beta for each company in 2023
    for index, row in df.iterrows():
        company_ticker = row['Company Ticker']
        market_ticker = row['Market Ticker']
        company_id = row['CompanyID']
        
        company_data = yf.download(company_ticker, start=start_date, end=end_date)
        market_data = yf.download(market_ticker, start=start_date, end=end_date)
        company_returns = company_data['Adj Close'].pct_change().dropna()
        market_returns = market_data['Adj Close'].pct_change().dropna()

        returns_data = pd.concat([company_returns, market_returns], axis=1).dropna()
        returns_data.columns = ['Company', 'Market']

        # beta formula: beta = covariance(Company, Market) / variance(Market)
        # measure of the volatility of an investment compared to the market 
        covariance = returns_data['Company'].cov(returns_data['Market'])
        market_variance = returns_data['Market'].var()
        beta = covariance / market_variance

        beta_results = beta_results._append({'CompanyID': company_id, 'Beta': beta}, 
                                            ignore_index=True)
        
    # Financial performance data calculated from financial reports
    # ESG Score from esg_scores table (will update ESG score again when other companies are added)
    esg_fin = {
        "CompanyID": [1, 2, 3, 4, 5, 6, 7, 8],
        "ROE": [1.558, 0.1975, 0.165, 0.3311, 0.2552, 0.04, 0.26, 0.1351],
        "ROA": [0.275, 0.0281, 0.0539, 0.0555, 0.1703, 0.034, 0.183, 0.0748],
        "DebtToEquity": [4.67, 6.03, 0.97, 4.98, 0.5, 0.25, 0.42, 0.8],
        "Total assets (thousands USD)": [352583000, 39256653, 45506507, 135241000, 229623000, 349053672, 402392000, 221370966]
    }
    esg_fin = pd.DataFrame(esg_fin)
    esg_fin = esg_fin.join(beta_results.set_index('CompanyID'), on='CompanyID', how='inner')
    esg_fin['CompanyID'] = esg_fin['CompanyID'].astype('category')

    esg_score_2023 = pd.DataFrame(fetch_ESG_financial_data(db_pool))
    esg_score_2023.rename(columns={'CompanyID': 'CompanyID_ESG'}, inplace=True)
    esg_fin = esg_fin.merge(esg_score_2023.set_index('CompanyID_ESG'), 
                           left_on='CompanyID', right_on='CompanyID_ESG', how='inner')

    esg_fin_metrics = esg_fin.drop(columns=['CompanyID'])
    correlation_matrix = esg_fin_metrics.corr(method='pearson')
    print(correlation_matrix) 

'''
high negative correlation between beta and ESG Score 2023
- higher beta, more risk, lower ESG score
'''
if __name__ == "__main__":
    main()

