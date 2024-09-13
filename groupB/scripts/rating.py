import numpy as np
import pandas as pd

# Example ESG data for a company
company_esg_data = {
    'ghg_emissions': 10000,  # in tons
    'energy_consumption': 500000,  # in kWh
    'waste_generated': 200,  # in tons
    'employee_count': 200,
    'employee_diversity_percentage': 35  # %
}

# Example industry benchmarks
industry_benchmarks = {
    'ghg_emissions_per_employee': 60,  # tons per employee
    'energy_consumption_per_employee': 3000,  # kWh per employee
    'waste_per_employee': 1.2,  # tons per employee
    'employee_diversity': 45  # % average for the industry
}


# Assigning weights to each ESG category
weights = {
    'environmental': 0.4,
    'social': 0.4,
    'governance': 0.2
}

# Function to calculate ESG score
def calculate_esg_score(company_data, benchmarks, weights):
    scores = {}

    # Environmental Score Calculation
    ghg_per_employee = company_data['ghg_emissions'] / company_data['employee_count']
    energy_per_employee = company_data['energy_consumption'] / company_data['employee_count']
    waste_per_employee = company_data['waste_generated'] / company_data['employee_count']
    
    # Normalize environmental scores against industry benchmarks
    scores['ghg_score'] = (benchmarks['ghg_emissions_per_employee'] - ghg_per_employee) / benchmarks['ghg_emissions_per_employee'] * 100
    scores['energy_score'] = (benchmarks['energy_consumption_per_employee'] - energy_per_employee) / benchmarks['energy_consumption_per_employee'] * 100
    scores['waste_score'] = (benchmarks['waste_per_employee'] - waste_per_employee) / benchmarks['waste_per_employee'] * 100
    
    # Average environmental score
    environmental_score = (scores['ghg_score'] + scores['energy_score'] + scores['waste_score']) / 3

    # Social Score Calculation
    employee_diversity_score = (company_data['employee_diversity_percentage'] / benchmarks['employee_diversity']) * 100
    
    # Final ESG Score
    final_esg_score = (environmental_score * weights['environmental']) + (employee_diversity_score * weights['social'])
    
    return final_esg_score

# Calculate the ESG score for the company
final_esg_score = calculate_esg_score(company_esg_data, industry_benchmarks, weights)

print(f"Final ESG Score: {final_esg_score:.2f}")