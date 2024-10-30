from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import pandas as pd
from scripts.db_connect import get_connection_pool, fetch_environmental_data, fetch_social_data, fetch_governance_data, fetch_ESG_data, fetch_predict_data, fetch_company_info, update_table, update_predict_table
from scripts.esg_score import calculate_environmental_score, calculate_social_score, calculate_governance_score, decimal_to_float
from scripts.predict import generate_predictions
from scripts.esg_commentary import analyze_trend_with_template
import uvicorn

# pip install fastapi
# pip install uvicorn
# pip install pandas
# pip install numpy
# pip install statsmodels

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_pool = get_connection_pool()

@app.get("/")
async def root():
    return {"message": "Pioneer Python API"}

@app.post("/calculate-esg")
async def calculate_esg():
    try:
        # Fetch data from database
        env_data = pd.DataFrame(fetch_environmental_data(db_pool))
        social_data = pd.DataFrame(fetch_social_data(db_pool))
        gov_data = pd.DataFrame(fetch_governance_data(db_pool))
        
        # Prepare pax data
        pax = social_data[['CompanyID', 'EmployeeCount', 'ReportYear']].copy()
        pax['EmployeeCount'] = pax['EmployeeCount'].apply(decimal_to_float)
        pax.dropna(inplace=True)
        
        # Calculate scores
        environmental_score = calculate_environmental_score(env_data, pax)
        social_score = calculate_social_score(social_data)
        governance_score = calculate_governance_score(gov_data)
        
        # Combine and calculate final ESG score
        esg_score = pd.DataFrame({
            'CompanyID': env_data['CompanyID'],
            'ReportYear': env_data['ReportYear'],
            'Environmental_Score': environmental_score,
            'Social_Score': social_score,
            'Governance_Score': governance_score
        })
        
        esg_score['Final_ESG_score'] = (
            esg_score['Environmental_Score'] * 0.35 +
            esg_score['Social_Score'] * 0.45 +
            esg_score['Governance_Score'] * 0.20
        )
        
        # Update database
        update_table(db_pool, esg_score, 'esg_scores')
        
        return {"message": "ESG scores calculated and updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
async def predict_esg():
    try:
        esg_score = fetch_ESG_data(db_pool)
        predictions_df = generate_predictions(esg_score)
        update_predict_table(db_pool, predictions_df)
        
        return {"message": "ESG predictions generated and updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/analysis/{company_id}")
async def get_commentary(company_id: int):
    try:
        # Fetch required data
        esg_scores_df = pd.DataFrame(fetch_predict_data(db_pool))
        company_info_df = pd.DataFrame(fetch_company_info(db_pool))
        
        # Check if company exists
        if company_id not in company_info_df['CompanyID'].values:
            raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
        
        # Generate commentary
        commentary = analyze_trend_with_template(esg_scores_df, company_id, company_info_df)
        
        return {"commentary": commentary}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5106)