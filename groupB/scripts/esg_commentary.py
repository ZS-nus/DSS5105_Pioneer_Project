import pandas as pd
import random
from db_connect import get_connection_pool, fetch_predict_data, fetch_company_info

# Create a connection pool
db_pool = get_connection_pool()

# Fetch data
esg_scores_df = pd.DataFrame(fetch_predict_data(db_pool))
company_info_df = pd.DataFrame(fetch_company_info(db_pool))

# Descriptive templates for improvement
improvement_templates = [
    "From {start_year} to {end_year}, {company_name}'s ESG score improved from {start_score:.2f} to {end_score:.2f}. "
    "Future predictions suggest that the score is expected to {predicted_trend} until {last_pred_year}.",
    
    "Between {start_year} and {end_year}, {company_name}'s ESG performance improved significantly, growing from {start_score:.2f} to {end_score:.2f}. "
    "This trend is projected to {predicted_trend} in the coming years, with continuous positive momentum.",
    
    "Over the years {start_year} to {end_year}, {company_name} achieved a notable increase in ESG score, rising from {start_score:.2f} to {end_score:.2f}. "
    "Forecasts indicate that this upward trend will {predicted_trend} until {last_pred_year}.",
    
    "From {start_year} to {end_year}, {company_name} experienced a consistent growth in ESG score, moving from {start_score:.2f} to {end_score:.2f}. "
    "The score is expected to {predicted_trend} further, reflecting the company's commitment to sustainability."
]

# Descriptive templates for decline
decline_templates = [
    "From {start_year} to {end_year}, {company_name}'s ESG score declined from {start_score:.2f} to {end_score:.2f}. "
    "Predictions suggest a continued {predicted_trend} until {last_pred_year}, reflecting challenges in sustainability efforts.",
    
    "Between {start_year} and {end_year}, {company_name} experienced a drop in ESG performance, with scores falling from {start_score:.2f} to {end_score:.2f}. "
    "Future trends predict that this decline will {predicted_trend} over the forecast period.",
    
    "Over the years {start_year} to {end_year}, {company_name}'s ESG performance declined, with scores dropping from {start_score:.2f} to {end_score:.2f}. "
    "The trend is projected to {predicted_trend} in the years ahead.",
    
    "From {start_year} to {end_year}, {company_name}'s ESG score decreased from {start_score:.2f} to {end_score:.2f}. "
    "The score is predicted to {predicted_trend} further, highlighting the need for immediate intervention."
]

# Descriptive templates for fluctuation
fluctuation_templates = [
    "Between {start_year} and {end_year}, {company_name} experienced fluctuations in ESG performance, "
    "with a peak score of {max_score:.2f} in {max_year} and a low of {min_score:.2f} in {min_year}. "
    "Future projections suggest the score may {predicted_trend} until {last_pred_year}.",
    
    "From {start_year} to {end_year}, {company_name}'s ESG performance showed variability, "
    "reaching a high of {max_score:.2f} in {max_year} and a low of {min_score:.2f} in {min_year}. "
    "Predictions indicate that this trend may {predicted_trend} in the forecast period.",
    
    "Over the years {start_year} to {end_year}, {company_name}'s ESG scores fluctuated, peaking at {max_score:.2f} in {max_year} and hitting a low of {min_score:.2f} in {min_year}. "
    "The future trend is expected to {predicted_trend}, reflecting potential challenges and opportunities.",
    
    "From {start_year} to {end_year}, {company_name} experienced variations in ESG performance, with the highest score at {max_score:.2f} in {max_year} and the lowest at {min_score:.2f} in {min_year}. "
    "Future predictions suggest the score may {predicted_trend} in the coming years."
]

# ESG component analysis templates
esg_analysis_templates = [
    "The {strongest_component} component shows the greatest improvement, primarily due to progress in {strongest_metric}. "
    "Meanwhile, the {weakest_component} component lags, particularly in {weakest_metric}. Strengthening {weakest_component} initiatives could yield significant benefits for {company_name}.",
    
    "In the predicted years, the most notable progress is seen in the {strongest_component} component, driven by {strongest_metric}. "
    "However, {weakest_component} remains a concern, with limited growth in {weakest_metric}. Targeted strategies could enhance performance for {company_name}.",
    
    "During the forecast period, {company_name} achieved its strongest improvement in the {strongest_component} component, driven by gains in {strongest_metric}. "
    "However, progress in {weakest_component}, particularly in {weakest_metric}, has been limited, requiring focused efforts.",
    
    "The forecast highlights notable improvements in the {strongest_component} component, especially in {strongest_metric}. "
    "At the same time, the {weakest_component} component, particularly in {weakest_metric}, shows room for growth. Strategic focus on these areas could strengthen {company_name}'s ESG performance.",
    
    "In the predicted years, {company_name}'s strongest progress is seen in the {strongest_component} component, supported by improvements in {strongest_metric}. "
    "However, limited progress in {weakest_component}, particularly in {weakest_metric}, suggests opportunities for targeted improvements."
]

# Trend analysis function with ESG component analysis
def analyze_trend_with_template(esg_scores_df, company_id, company_info_df):
    group = esg_scores_df[esg_scores_df['CompanyID'] == company_id].sort_values('Year')
    actual_group = group[group['Data_Type'] == 'Actual']
    predicted_group = group[group['Data_Type'] == 'Predicted']
    
    # Fetch company name
    company_name = company_info_df[company_info_df['CompanyID'] == company_id]['CompanyName'].values[0]

    # Actual data points
    scores = actual_group['ESG_Score'].values
    years = actual_group['Year'].values

    # Predicted data points
    pred_years = predicted_group['Year'].values if not predicted_group.empty else []
    pred_scores = predicted_group['ESG_Score'].values if not predicted_group.empty else []
    pred_env = predicted_group['Environmental'].values if not predicted_group.empty else []
    pred_soc = predicted_group['Social'].values if not predicted_group.empty else []
    pred_gov = predicted_group['Governance'].values if not predicted_group.empty else []

    # Get basic data
    start_year, end_year = years[0], years[-1]
    start_score, end_score = scores[0], scores[-1]
    max_score, max_year = max(scores), years[scores.argmax()]
    min_score, min_year = min(scores), years[scores.argmin()]

    # Determine predicted trend
    if len(pred_scores) > 1:
        if all(x < y for x, y in zip(pred_scores, pred_scores[1:])):
            predicted_trend = "show steady improvement"
            templates = improvement_templates
        elif all(x > y for x, y in zip(pred_scores, pred_scores[1:])):
            predicted_trend = "decline"
            templates = decline_templates
        else:
            predicted_trend = "fluctuate"
            templates = fluctuation_templates
        last_pred_year = pred_years[-1]
    else:
        predicted_trend = "remain uncertain"
        templates = fluctuation_templates
        last_pred_year = "the foreseeable future"

    # Randomly select a template for the first paragraph
    selected_template = random.choice(templates)

    # Fill in the first paragraph
    description = selected_template.format(
        company_name=company_name,
        start_year=start_year,
        end_year=end_year,
        start_score=start_score,
        end_score=end_score,
        max_year=max_year,
        max_score=max_score,
        min_year=min_year,
        min_score=min_score,
        predicted_trend=predicted_trend,
        last_pred_year=last_pred_year
    )

    # ESG component analysis
    if len(pred_env) > 1 and len(pred_soc) > 1 and len(pred_gov) > 1:
        env_change = pred_env[-1] - pred_env[0]
        soc_change = pred_soc[-1] - pred_soc[0]
        gov_change = pred_gov[-1] - pred_gov[0]

        # Determine strongest and weakest components
        max_change = max(env_change, soc_change, gov_change)
        min_change = min(env_change, soc_change, gov_change)

        if max_change == env_change:
            strongest_component = "Environmental"
            strongest_metric = random.choice(['Energy Consumption', 'GHG Emissions', 'Water Usage', 'Waste Generated'])
        elif max_change == soc_change:
            strongest_component = "Social"
            strongest_metric = random.choice(['Data Security', 'Customer Privacy', 'Cyber Security', 'Gender', 'Age', 'Work Related Injuries', 'Training Hours'])
        else:
            strongest_component = "Governance"
            strongest_metric = random.choice(['Board Composition', 'Ethical Behaviour', 'Risk Management', 'Certification'])

        if min_change == env_change:
            weakest_component = "Environmental"
            weakest_metric = random.choice(['Energy Consumption', 'GHG Emissions', 'Water Usage', 'Waste Generated'])
        elif min_change == soc_change:
            weakest_component = "Social"
            weakest_metric = random.choice(['Data Security', 'Customer Privacy', 'Cyber Security', 'Gender', 'Age', 'Work Related Injuries', 'Training Hours'])
        else:
            weakest_component = "Governance"
            weakest_metric = random.choice(['Board Composition', 'Ethical Behaviour', 'Risk Management', 'Certification'])

        # Randomly select a template for ESG component analysis
        esg_analysis = random.choice(esg_analysis_templates).format(
            strongest_component=strongest_component,
            strongest_metric=strongest_metric,
            weakest_component=weakest_component,
            weakest_metric=weakest_metric,
            company_name=company_name
        )
    else:
        esg_analysis = "Due to limited prediction data, component-specific analysis could not be performed."

    # Return the final description
    return description + " " + esg_analysis

# Test the function
company_id = 2  # Replace with the appropriate CompanyID
result = analyze_trend_with_template(esg_scores_df, company_id, company_info_df)
print(result)
