import pandas as pd
import random
import numpy as np
from .db_connect import get_connection_pool, fetch_env_score_data, fetch_company_info

# Create a connection pool
db_pool = get_connection_pool()

# Fetch data
env_scores_df = pd.DataFrame(fetch_env_score_data(db_pool))
company_info_df = pd.DataFrame(fetch_company_info(db_pool))

def get_trend_description(start, end, threshold=0.5):
    """Generate detailed trend description based on magnitude of change"""
    change = end - start
    abs_change = abs(change)
    
    if abs_change < threshold:
        return "remained relatively stable"
    elif abs_change < threshold * 2:
        return "slightly " + ("improved" if change > 0 else "declined")
    elif abs_change < threshold * 3:
        return "significantly " + ("improved" if change > 0 else "declined")
    else:
        return "dramatically " + ("improved" if change > 0 else "declined")

def get_performance_level(score):
    """Categorize performance level based on score"""
    if score >= 8:
        return "excellent"
    elif score >= 6:
        return "good"
    elif score >= 4:
        return "moderate"
    else:
        return "needs improvement"

def calculate_year_over_year_change(data, metric):
    """Calculate year-over-year changes for a metric"""
    changes = data[metric].diff()
    return changes.mean(), changes.std()

def generate_detailed_recommendation(metric, score, trend, volatility):
    """Generate specific recommendations based on metric performance and trends"""
    base_recommendations = {
        'Energy Consumption': {
            'poor_trending_down': [
                "Urgent need to implement energy efficiency measures. Consider conducting an energy audit.",
                "Investigate renewable energy alternatives and develop a comprehensive energy management plan."
            ],
            'poor_trending_up': [
                "Continue improving energy efficiency measures. Consider setting more ambitious targets.",
                "Explore additional renewable energy opportunities and energy-saving technologies."
            ],
            'good_trending_down': [
                "Review recent changes in energy consumption patterns to identify causes of decline.",
                "Reinforce successful energy management practices and consider new efficiency measures."
            ],
            'good_trending_up': [
                "Maintain current energy management practices while exploring innovative solutions.",
                "Consider sharing best practices and setting industry-leading targets."
            ]
        },
        # Add similar detailed recommendations for other metrics
    }
    
    performance_category = 'good' if score >= 6 else 'poor'
    trend_category = 'trending_up' if trend > 0 else 'trending_down'
    key = f"{performance_category}_{trend_category}"
    
    recommendations = base_recommendations.get(metric, {}).get(key, [])
    if volatility > 0.5:
        recommendations.append("Consider implementing more consistent measurement and management practices to reduce volatility.")
    
    return random.choice(recommendations) if recommendations else "Consider implementing targeted improvement measures."

def analyze_env_metrics(company_id):
    try:
        company_data = env_scores_df[env_scores_df['CompanyID'] == company_id].sort_values('ReportYear')
        if company_data.empty:
            return "No environmental data available for this company."

        company_name = company_data['CompanyName'].iloc[0]
        start_year = company_data['ReportYear'].iloc[0]
        end_year = company_data['ReportYear'].iloc[-1]

        metrics = {
            'Energy Consumption': 'EnergyConsumption_score',
            'GHG Emissions': 'GHGEmissions_score',
            'Water Usage': 'WaterUsage_score',
            'Waste Generated': 'WasteGenerated_score'
        }

        analysis_results = {}
        for metric_name, column in metrics.items():
            start_value = company_data[column].iloc[0]
            end_value = company_data[column].iloc[-1]
            mean_change, std_change = calculate_year_over_year_change(company_data, column)
            trend_description = get_trend_description(start_value, end_value)
            performance_level = get_performance_level(end_value)
            
            analysis_results[metric_name] = {
                'score': end_value,
                'trend': trend_description,
                'performance': performance_level,
                'recommendation': generate_detailed_recommendation(
                    metric_name, end_value, mean_change, std_change
                )
            }

        strongest = max(analysis_results.items(), key=lambda x: x[1]['score'])
        weakest = min(analysis_results.items(), key=lambda x: x[1]['score'])

        # Shorter, more concise analysis
        analysis = f"{company_name}'s Environmental Performance ({start_year}-{end_year}):\n\n"
        
        # Only show significant changes and issues that need attention
        for metric, results in analysis_results.items():
            if results['performance'] in ['needs improvement', 'excellent'] or 'significantly' in results['trend']:
                analysis += f"• {metric}: {results['trend'].capitalize()}. {results['performance'].capitalize()}.\n"

        analysis += f"\nHighlights:\n"
        analysis += f"• Leading in {strongest[0]} ({strongest[1]['performance']})\n"
        analysis += f"• Focus needed on {weakest[0]} ({weakest[1]['performance']})\n"
        analysis += f"\nKey Recommendation: {weakest[1]['recommendation']}"

        return analysis

    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while analyzing environmental metrics."

# Test the function
# company_id = 1
# result = analyze_env_metrics(company_id)
# print(result)

