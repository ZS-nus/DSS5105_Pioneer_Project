import yfinance as yf
import pandas as pd
import scipy.stats as stats
from db_connect import get_connection_pool, fetch_ESG_score_2023, update_table, fetch_2023_finances

def get_company_tickers():
    return {
        4: {'ticker': 'IBM', 'market': '^GSPC', 'currency': 'USD'},
        6: {'ticker': '005930.KS', 'market': '^KS11', 'currency': 'KRW'},
        2: {'ticker': '0992.HK', 'market': '^HSI', 'currency': 'HKD'},
        5: {'ticker': 'META', 'market': '^GSPC', 'currency': 'USD'},
        3: {'ticker': '1810.HK', 'market': '^HSI', 'currency': 'HKD'},
        7: {'ticker': 'GOOGL', 'market': '^GSPC', 'currency': 'USD'},
        8: {'ticker': '0700.HK', 'market': '^HSI', 'currency': 'HKD'},
        1: {'ticker': 'AAPL', 'market': '^GSPC', 'currency': 'USD'}
    }

def calculate_financial_metrics(start_date='2023-01-01', end_date='2023-12-31'):
    companies = get_company_tickers()
    financial_results = pd.DataFrame(columns=['CompanyID', 'Beta', 'Mean_stockprice', 
                                            'Yearend_stockprice', 'Currency'])
    
    for company_id, info in companies.items():
        try:
            company_data = yf.download(info['ticker'], start=start_date, end=end_date)
            market_data = yf.download(info['market'], start=start_date, end=end_date)
            
            company_returns = company_data['Adj Close'].pct_change().dropna()
            market_returns = market_data['Adj Close'].pct_change().dropna()
            returns_data = pd.concat([company_returns, market_returns], axis=1).dropna()
            returns_data.columns = ['Company', 'Market']
            
            yearend_stockprice = company_data['Adj Close'].iloc[-1]
            mean_stockprice = company_data['Adj Close'].mean()
            
            covariance = returns_data['Company'].cov(returns_data['Market'])
            market_variance = returns_data['Market'].var()
            beta = covariance / market_variance
            
            financial_results = financial_results._append({
                'CompanyID': company_id,
                'Beta': beta,
                'Mean_stockprice': mean_stockprice,
                'Yearend_stockprice': yearend_stockprice,
                'Currency': info['currency']
            }, ignore_index=True)
            
        except Exception as e:
            print(f"Error processing company {info['ticker']}: {str(e)}")
            
    return financial_results.sort_values(by='CompanyID').reset_index(drop=True)

def calculate_correlations(esg_fin_metrics):
    corr_matrix = esg_fin_metrics.corr(method='pearson')['Final_ESG_Score']
    return corr_matrix.reset_index()

def calculate_p_values(esg_fin_metrics):
    p_values = {}
    for column in esg_fin_metrics.columns:
        if column != 'Final_ESG_Score':
            corr_coeff, p_value = stats.pearsonr(
                esg_fin_metrics['Final_ESG_Score'], 
                esg_fin_metrics[column]
            )
            p_values[column] = p_value
    return p_values

async def update_financial_metrics(db_pool):
    try:
        financial_results = calculate_financial_metrics()
        esg_score_2023 = pd.DataFrame(fetch_ESG_score_2023(db_pool)).sort_values(by='CompanyID')
        esg_fin = pd.DataFrame(fetch_2023_finances(db_pool)).sort_values(by='CompanyID')
        
        esg_fin[['Final_ESG_Score']] = esg_score_2023[['Final_ESG_Score']]
        esg_fin[['Beta', 'Mean_stockprice', 'Yearend_stockprice', 'Currency']] = financial_results[
            ['Beta', 'Mean_stockprice', 'Yearend_stockprice', 'Currency']
        ]
        
        esg_fin_metrics = esg_fin[[
            'ROA', 'ROE', 'DebtToEquity', 'TotalAssets_thousandsUSD', 
            'Beta', 'Final_ESG_Score'
        ]].astype(float)
        
        corr_matrix = calculate_correlations(esg_fin_metrics)
        p_values = calculate_p_values(esg_fin_metrics)
        
        update_table(db_pool, esg_fin, 'esg_fin')
        update_table(db_pool, corr_matrix, 'corr_matrix')
        
        return {
            'correlation_matrix': corr_matrix.to_dict('records'),
            'p_values': p_values,
            'financial_metrics': esg_fin.to_dict('records')
        }
        
    except Exception as e:
        raise Exception(f"Error updating financial metrics: {str(e)}")
