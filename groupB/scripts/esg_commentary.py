import pandas as pd
import random
from db_connect import get_connection_pool, fetch_predict_data, fetch_company_info

# Create a connection pool
db_pool = get_connection_pool()

# Fetch data
esg_scores_df = pd.DataFrame(fetch_predict_data(db_pool))
company_info_df = pd.DataFrame(fetch_company_info(db_pool)) 

# print(esg_scores_df.head())

# Descriptive templates split by trend type
improvement_templates = [
    "From {start_year} to {end_year}, {company_name}'s ESG score improved from {start_score:.2f} to {end_score:.2f}. "
    "Based on this trend, future predictions suggest that the score is expected to {predicted_trend} until {last_pred_year}. This indicates that company {company_name} is likely to continue capitalizing on opportunities to further enhance its ESG performance.",

    "Between {start_year} and {end_year}, {company_name}'s ESG performance improved from {start_score:.2f} to {end_score:.2f}. "
    "Looking ahead, predictions show that the company's ESG score may {predicted_trend} through {last_pred_year}. This forecast suggests potential growth in sustainability efforts, influenced by factors such as regulatory changes, market demand for green products, and technological advancements."
]

decline_templates = [
    "Between {start_year} and {end_year}, {company_name}'s ESG performance declined from {start_score:.2f} to {end_score:.2f}. "
    "Predictions indicate a continued {predicted_trend} until {last_pred_year}, reflecting potential challenges in sustainability efforts, such as increased regulatory pressure, limited access to green technologies, or rising operational costs.",

    "From {start_year} to {end_year}, {company_name} experienced a decline in its ESG score from {start_score:.2f} to {end_score:.2f}. "
    "Looking ahead, predictions suggest a {predicted_trend} until {last_pred_year}, signaling future challenges for ESG performance, such as adapting to stricter environmental regulations or addressing stakeholder concerns over sustainability."
]

fluctuation_templates = [
    "Over the course of {start_year} to {end_year}, {company_name} has {trend_description}, achieving a peak score of {max_score:.2f} in {max_year} and a lowest score of {min_score:.2f} in {min_year}. "
    "Future projections suggest the score may {predicted_trend} until {last_pred_year}, indicating potential shifts in the company's approach to ESG practices, such as adopting new sustainability technologies, improving supply chain transparency, or enhancing employee well-being initiatives.",

    "From {start_year} to {end_year}, {company_name} experienced {trend_description} in its ESG score, peaking in {max_year} with a score of {max_score:.2f}, and reaching a low in {min_year} with a score of {min_score:.2f}. "
    "Projections suggest that by {last_pred_year}, the score may {predicted_trend}, signaling future opportunities or challenges for company {company_name} in terms of ESG performance, such as leveraging renewable energy initiatives or responding to evolving consumer expectations."
]

# Trend analysis with grouped template selection
def analyze_trend_with_template(esg_scores_df, company_id, company_info_df):
    group = esg_scores_df[esg_scores_df['CompanyID'] == company_id].sort_values('Year')
    actual_group = group[group['Data_Type'] == 'Actual']
    predicted_group = group[group['Data_Type'] == 'Predicted']
    
    # Fetch company name from company_info_df
    company_name = company_info_df[company_info_df['CompanyID'] == company_id]['CompanyName'].values[0]

    # Actual data points
    scores = actual_group['ESG_Score'].values
    years = actual_group['Year'].values

    # Predicted data points
    pred_years = predicted_group['Year'].values if not predicted_group.empty else []
    pred_scores = predicted_group['ESG_Score'].values if not predicted_group.empty else []

    # Get basic data from actual data
    start_year, end_year = years[0], years[-1]
    start_score, end_score = scores[0], scores[-1]
    max_score, max_year = max(scores), years[scores.argmax()]
    min_score, min_year = min(scores), years[scores.argmin()]

    # Predicted trend
    if len(pred_scores) > 1:
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

    # Actual trend
    if all(x < y for x, y in zip(scores, scores[1:])):
        trend_description = "showed consistent improvement"
        templates = improvement_templates
    elif all(x > y for x, y in zip(scores, scores[1:])):
        trend_description = "experienced a decline"
        templates = decline_templates
    else:
        trend_description = "fluctuated over time"
        templates = fluctuation_templates

    # Randomly select one template from the appropriate group
    selected_template = random.choice(templates)

    # Ensure all placeholders are properly filled, including company_name
    description = selected_template.format(
        company_name=company_name,  # Use company name in the description
        start_year=start_year,
        end_year=end_year,
        start_score=start_score,
        end_score=end_score,
        max_year=max_year,
        max_score=max_score,
        min_year=min_year,
        min_score=min_score,
        predicted_trend=predicted_trend,
        trend_description=trend_description,
        last_pred_year=last_pred_year
    )

    return description

# Test the function
# company_id = 2 # example
# result = analyze_trend_with_template(esg_scores_df, company_id, company_info_df)
# print(result)
