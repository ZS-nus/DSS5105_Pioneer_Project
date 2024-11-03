import yfinance as yf
import pandas as pd
from db_connect import get_connection_pool, fetch_ESG_score_2023, update_table, fetch_2023_finances


def main():
    db_pool = get_connection_pool()
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

    df['Currency'] = [
        'USD', 
        'KRW',
        'HKD',
        'USD',
        'HKD',
        'USD',
        'HKD',
        'USD'    
    ]
    
    # Year 2023
    start_date = '2023-01-01'
    end_date = '2023-12-31'

    financial_results = pd.DataFrame(columns=['CompanyID', 'Beta', 'Mean_stockprice', 
                                          'Yearend_stockprice', 'Currency'])
    
    # Calculate beta for each company in 2023
    for index, row in df.iterrows():
        company_ticker = row['Company Ticker']
        market_ticker = row['Market Ticker']
        company_id = row['CompanyID']
        stock_currency = row['Currency']
        
        company_data = yf.download(company_ticker, start=start_date, end=end_date)
        market_data = yf.download(market_ticker, start=start_date, end=end_date)
        
        # Daily returns
        company_returns = company_data['Adj Close'].pct_change().dropna()
        market_returns = market_data['Adj Close'].pct_change().dropna()
        returns_data = pd.concat([company_returns, market_returns], axis=1).dropna()
        returns_data.columns = ['Company', 'Market']
        
        # Stock price
        yearend_stockprice = company_data['Adj Close'].iloc[-1,0] # year end price
        mean_stockprice = company_data['Adj Close'].mean().tolist()[0] # mean stock price

        # beta formula: beta = covariance(Company, Market) / variance(Market)
        # measure of the volatility of an investment compared to the market 
        covariance = returns_data['Company'].cov(returns_data['Market'])
        market_variance = returns_data['Market'].var()
        beta = covariance / market_variance

        financial_results = financial_results._append({'CompanyID': company_id, 'Beta': beta, 
                                                   'Mean_stockprice': mean_stockprice,
                                                   'Yearend_stockprice': yearend_stockprice,
                                                   'Currency': row['Currency']}, 
                                                    ignore_index=True)
        financial_results.sort_values(by='CompanyID', inplace=True)
        financial_results.reset_index(drop=True, inplace=True)
        # financial_results = financial_results[['Beta', 'Mean_stockprice', 'Yearend_stockprice', 'Currency']]       
    
    # Update ESG and financial performance data in db
    esg_score_2023 = pd.DataFrame(fetch_ESG_score_2023(db_pool)).sort_values(by='CompanyID')
    esg_fin = pd.DataFrame(fetch_2023_finances(db_pool)).sort_values(by='CompanyID')
    
    esg_fin[['Final_ESG_Score']] = esg_score_2023[['Final_ESG_Score']]
    esg_fin[['Beta', 'Mean_stockprice', 'Yearend_stockprice', 'Currency']] = financial_results[['Beta', 'Mean_stockprice', 'Yearend_stockprice', 'Currency']]
    
    '''
    high negative correlation between beta and ESG Score 2023
    - higher beta, more risk, lower ESG score
    '''
    esg_fin_metrics = esg_fin[['ROA', 'ROE', 'DebtToEquity', 'TotalAssets_thousandsUSD', 'Beta','Final_ESG_Score']]
    corr_matrix = esg_fin_metrics.corr(method='pearson')['Final_ESG_Score']
    corr_matrix = corr_matrix.reset_index()
    
    update_table(db_pool, esg_fin, 'esg_fin')
    update_table(db_pool, corr_matrix, 'corr_matrix')
    print(corr_matrix)

if __name__ == "__main__":
    main()