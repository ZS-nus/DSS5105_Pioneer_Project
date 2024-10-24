import random
import pandas as pd
from db_connect import connect_to_db, fetch_ESG_data, fetch_predict_data

# 连接数据库
db_pool = connect_to_db()
if not db_pool:
    print("Failed to connect to the database.")
    exit()

# 获取历史数据 'CompanyID'，'ReportYear' ，'Environmental_Score' ，'Social_Score' ，'Governance_Score'，'Final_ESG_score'
historical_data = pd.DataFrame(fetch_ESG_data(db_pool))
# 重命名 historical_data 列，使列名与 predicted_data 的列名一致，便于分析
historical_data.rename(columns={
    'ReportYear': 'Year',
    'Environmental_Score': 'Environmental',
    'Social_Score': 'Social',
    'Governance_Score': 'Governance',
    'Final_ESG_score': 'ESG_Score'
}, inplace=True)


#预测数据 'CompanyID', 'Year', 'Environmental', 'Social', 'Governance', 'ESG_Score', 'Data_Type'
predicted_data = pd.DataFrame(fetch_predict_data(db_pool))


# Descriptive templates categorized by trend
improvement_templates = [
    "From {start_year} to {end_year}, company {company_id}'s ESG score {trend_description}, peaking in {max_year} at {max_score:.2f}. "
    "Based on this trend, future predictions suggest that the score is likely to {predicted_trend} until {last_pred_year}. This indicates that company {company_id} may continue to face challenges or opportunities in its ESG performance.",

    "Between {start_year} and {end_year}, company {company_id}'s ESG performance {trend_description}, reaching its highest in {max_year} at {max_score:.2f}. "
    "Looking ahead, predictions show that the company's ESG score may {predicted_trend} through {last_pred_year}. This forecast reflects potential shifts in sustainability efforts and external factors."
]

decline_templates = [
    "Between {start_year} and {end_year}, company {company_id}'s ESG performance {trend_description}. "
    "Predictions indicate a continued {predicted_trend} until {last_pred_year}, reflecting potential challenges in sustainability efforts.",

    "From {start_year} to {end_year}, company {company_id} experienced {trend_description} in its ESG score. "
    "Looking ahead, predictions suggest a {predicted_trend} until {last_pred_year}, signaling future challenges for ESG performance."
]

fluctuation_templates = [
    "Over the course of {start_year} to {end_year}, company {company_id} has {trend_description}, achieving a peak score of {max_score:.2f} in {max_year}. "
    "Future projections suggest the score may {predicted_trend} until {last_pred_year}, indicating potential shifts in the company's approach to ESG practices.",

    "From {start_year} to {end_year}, company {company_id} experienced {trend_description} in its ESG score, peaking in {max_year} with a score of {max_score:.2f}. "
    "Projections suggest that by {last_pred_year}, the score may {predicted_trend}, signaling future opportunities or challenges for company {company_id} in terms of ESG performance."
]

def analyze_trend_with_template(historical_data, predicted_data, company_id):
    # 筛选特定公司的历史数据和预测数据
    historical_company_data = historical_data[historical_data['CompanyID'] == company_id].sort_values('Year')
    predicted_company_data = predicted_data[predicted_data['CompanyID'] == company_id].sort_values('Year')

    # 提取历史数据点
    scores = historical_company_data['ESG_Score'].values
    years = historical_company_data['Year'].values

    # 提取预测数据点
    pred_years = predicted_company_data['Year'].values
    pred_scores = predicted_company_data['ESG_Score'].values

    # 获取历史数据的基本信息
    start_year, end_year = years[0], years[-1]
    start_score, end_score = scores[0], scores[-1]
    max_score, max_year = max(scores), years[scores.argmax()]

    # 分析预测趋势
    if len(pred_scores) > 1:
        # 检查预测数据是否呈现出稳定的上升、下降或波动趋势
        if all(x < y for x, y in zip(pred_scores, pred_scores[1:])):
            predicted_trend = "show steady improvement"
        elif all(x > y for x, y in zip(pred_scores, pred_scores[1:])):
            predicted_trend = "show gradual decline"
        else:
            predicted_trend = "experience fluctuations"
        last_pred_year = pred_years[-1]
    else:
        predicted_trend = "remain uncertain"
        last_pred_year = "the foreseeable future"

    # 分析历史趋势
    if all(x < y for x, y in zip(scores, scores[1:])):
        trend_description = "showed consistent improvement"
        suitable_templates = improvement_templates
    elif all(x > y for x, y in zip(scores, scores[1:])):
        trend_description = "experienced a gradual decline"
        suitable_templates = decline_templates
    else:
        trend_description = "fluctuated over time"
        suitable_templates = fluctuation_templates

    # 随机选择一个适合的模板
    selected_template = random.choice(suitable_templates)

    # 使用模板生成描述
    description = selected_template.format(
        company_id=company_id,
        start_year=start_year,
        end_year=end_year,
        start_score=start_score,
        end_score=end_score,
        max_year=max_year,
        max_score=max_score,
        predicted_trend=predicted_trend,
        trend_description=trend_description,
        last_pred_year=last_pred_year
    )

    return description


# Test the function
company_id = 1  # example
description = analyze_trend_with_template(historical_data, predicted_data, company_id)
print(description)
