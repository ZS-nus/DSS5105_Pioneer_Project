import pandas as pd
import random
from db_connect import connect_to_db, fetch_ESG_data, fetch_predict_data
    
esg_scores_df = pd.DataFrame(fetch_predict_data(connect_to_db()))

# Descriptive templates with distinction
templates = [
    "From {start_year} to {end_year}, company {company_id}'s ESG score {trend_description}, peaking in {max_year} at {max_score:.2f}. "
    "Based on this trend, future predictions suggest that the score is likely to {predicted_trend} until {last_pred_year}. This indicates that company {company_id} may continue to face challenges or opportunities in its ESG performance.",

    "Between {start_year} and {end_year}, company {company_id}'s ESG performance {trend_description}, reaching its highest in {max_year} at {max_score:.2f}. "
    "Looking ahead, predictions show that the company's ESG score may {predicted_trend} through {last_pred_year}. This forecast reflects potential shifts in sustainability efforts and external factors.",

    "Over the course of {start_year} to {end_year}, company {company_id} has {trend_description}, achieving a peak score of {max_score:.2f} in {max_year}. "
    "Future projections suggest the score may {predicted_trend} until {last_pred_year}, indicating potential shifts in the company's approach to ESG practices.",

    "From {start_year} through {end_year}, the ESG score of company {company_id} {trend_description}, with the highest score being {max_score:.2f} in {max_year}. "
    "Looking ahead, predictions suggest the score will {predicted_trend} until {last_pred_year}, showing possible impacts of strategic ESG changes.",

    "Company {company_id} demonstrated {trend_description} between {start_year} and {end_year}, peaking in {max_year} at {max_score:.2f}. "
    "Based on this, predictions for the future indicate the score may {predicted_trend} through {last_pred_year}, reflecting potential sustainability shifts.",

    "Between {start_year} and {end_year}, company {company_id}'s ESG score {trend_description}, reaching a peak of {max_score:.2f} in {max_year}. "
    "Predictions for the future suggest the score could {predicted_trend} through {last_pred_year}, pointing to either challenges or improvements in ESG efforts.",

    "During the period from {start_year} to {end_year}, company {company_id} saw its ESG score {trend_description}, reaching its highest point in {max_year} at {max_score:.2f}. "
    "Looking ahead, predictions show the score may {predicted_trend} until {last_pred_year}, reflecting potential changes in the company's ESG strategy.",

    "From {start_year} to {end_year}, company {company_id} experienced {trend_description} in its ESG score, peaking in {max_year} with a score of {max_score:.2f}. "
    "Projections suggest that by {last_pred_year}, the score may {predicted_trend}, signaling future opportunities or challenges for company {company_id} in terms of ESG performance."
]

# Simplified trend analysis and random template selection
def analyze_trend_with_template(esg_scores, company_id):
    group = esg_scores[esg_scores['CompanyID'] == company_id].sort_values('Year')
    actual_group = group[group['Data_Type'] == 'Actual']
    predicted_group = group[group['Data_Type'] == 'Predicted']

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

    # Predicted trend
    if len(pred_scores) > 1:
        # Check if all predictions are steadily increasing, decreasing, or fluctuating
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
    elif all(x > y for x, y in zip(scores, scores[1:])):
        trend_description = "experienced a gradual decline"
    else:
        trend_description = "fluctuated over time"

    # Randomly select one template
    selected_template = random.choice(templates)

    # Ensure all placeholders are properly filled
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
result = analyze_trend_with_template(esg_scores_df, company_id)
print(result)
