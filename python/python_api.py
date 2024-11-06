from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import pandas as pd
from pathlib import Path
import os
from scripts.db_connect import get_connection_pool, fetch_environmental_data, fetch_social_data, fetch_governance_data, fetch_ESG_data, fetch_predict_data, fetch_company_info, update_table, update_predict_table
from scripts.esg_score import calculate_environmental_score, calculate_social_score, calculate_governance_score, decimal_to_float
from scripts.predict import generate_predictions
from scripts.esg_commentary import analyze_trend_with_template
from scripts.convert_pdf_text import PDFConverter
from scripts.storage_cleanup import StorageManager
import uvicorn
import schedule
import time
from threading import Thread
from scripts.fetch_report import FirebaseStorageManager
import logging
from scripts.report_extraction_text import ReportAnalyzer
from scripts.convert_pdf_table import process_pdf
import asyncio
from scripts.report_extraction_table import TableDataExtractor

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

# Initialize storage paths
STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(exist_ok=True)

# Initialize PDFConverter
pdf_converter = PDFConverter(STORAGE_DIR)

# Initialize storage manager
storage_manager = StorageManager(
    storage_dir="storage",
    max_age_days=7,    # Keep files for 7 days
    max_size_mb=500    # Keep maximum 500MB of files
)

# Initialize Firebase Storage Manager
firebase_manager = FirebaseStorageManager(
    credential_path='./scripts/pioneer_key.json',  # Adjust path as needed
    storage_dir=STORAGE_DIR
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pioneer_api')

# Add after other initializations
report_analyzer = ReportAnalyzer()

# Initialize the table extractor
table_extractor = TableDataExtractor()

def run_cleanup_schedule():
    """Run cleanup job on schedule"""
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour

# Schedule cleanup to run daily at midnight
schedule.every().day.at("00:00").do(storage_manager.cleanup)

# Start the cleanup scheduler in a separate thread
cleanup_thread = Thread(target=run_cleanup_schedule, daemon=True)
cleanup_thread.start()

@app.get("/")
async def root():
    return {"message": "Pioneer Python API"}

# Add cleanup check before processing new files
@app.post("/convert-to-text/{file_name}")
async def convert_to_text(file_name: str):
    """
    Convert PDF to text format with table extraction.
    Uses file_name from the path parameter to process PDF from storage.
    """
    try:
        # Run cleanup check before processing
        storage_manager.cleanup()
        
        # Validate file name and extension
        if not file_name.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file format. File must be a PDF."
            )
        
        # Construct paths
        pdf_path = STORAGE_DIR / "pdf_uploads" / file_name
        txt_filename = os.path.splitext(file_name)[0] + '.txt'
        
        # Check if PDF exists
        if not pdf_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"PDF file '{file_name}' not found in storage."
            )
        
        # Process PDF
        result = pdf_converter.process_pdf(str(pdf_path), txt_filename)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )
            
        return {
            "message": "PDF converted successfully",
            "original_filename": file_name,
            "pdf_path": result["pdf_path"],
            "txt_path": result["txt_path"]
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the PDF: {str(e)}"
        )

@app.post("/convert-pdf-table/{file_name}")
async def convert_pdf_table(file_name: str):
    """
    Convert PDF to text format with enhanced table extraction.
    Uses file_name from the path parameter to process PDF from storage.
    """
    try:
        # Run cleanup check before processing
        storage_manager.cleanup()
        
        # Validate file name and extension
        if not file_name.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file format. File must be a PDF."
            )
        
        # Construct paths
        pdf_path = STORAGE_DIR / "pdf_uploads" / file_name
        folder_name = os.path.splitext(file_name)[0]
        output_dir = STORAGE_DIR / "table_outputs" / folder_name
        
        # Check if PDF exists
        if not pdf_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"PDF file '{file_name}' not found in storage."
            )
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Process PDF with table extraction
        result = process_pdf(str(pdf_path), str(output_dir))
            
        return {
            "message": "PDF processed successfully with table extraction",
            "original_filename": file_name,
            "pdf_path": str(pdf_path),
            "tables_directory": str(output_dir),
            "table_count": result["table_count"],
            "table_files": result["table_files"]
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the PDF: {str(e)}"
        )

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
            esg_score['Environmental_Score'] * 0.4 +
            esg_score['Social_Score'] * 0.3 +
            esg_score['Governance_Score'] * 0.3
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

@app.post("/cleanup")
async def manual_cleanup(force: bool = True, max_age_hours: Optional[int] = None):
    """
    Manually trigger storage cleanup
    
    Args:
        force (bool): If True, forces deletion regardless of age/size limits
        max_age_hours (int, optional): If specified, only delete files older than this many hours
    """
    try:
        if force:
            # Force cleanup - delete everything or by age if specified
            result = storage_manager.force_cleanup(max_age_hours)
            return {
                "status": "success",
                "message": "Force cleanup completed",
                "details": result
            }
        else:
            # Regular cleanup using age/size limits
            result = storage_manager.cleanup()
            return {
                "status": "success",
                "message": "Regular cleanup completed",
                "details": result
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during cleanup: {str(e)}"
        )

# Optional: Add a separate force cleanup endpoint
@app.post("/cleanup/force")
async def force_cleanup(max_age_hours: Optional[int] = None):
    """Force cleanup all files or files older than specified hours"""
    try:
        result = storage_manager.force_cleanup(max_age_hours)
        return {
            "status": "success",
            "message": "Force cleanup completed",
            "details": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during force cleanup: {str(e)}"
        )

@app.get("/storage-status")
async def get_storage_status():
    """
    Get current storage usage statistics
    """
    try:
        pdf_size = storage_manager.get_directory_size(storage_manager.pdf_dir)
        txt_size = storage_manager.get_directory_size(storage_manager.txt_dir)
        total_size = pdf_size + txt_size
        
        # Count files
        pdf_files = len(list(storage_manager.pdf_dir.glob('*')))
        txt_files = len(list(storage_manager.txt_dir.glob('*')))
        
        return {
            "status": "success",
            "storage_info": {
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "pdf_directory": {
                    "size_mb": round(pdf_size / (1024 * 1024), 2),
                    "file_count": pdf_files
                },
                "txt_directory": {
                    "size_mb": round(txt_size / (1024 * 1024), 2),
                    "file_count": txt_files
                },
                "limits": {
                    "max_size_mb": storage_manager.max_size / (1024 * 1024),
                    "max_age_days": storage_manager.max_age.days
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting storage status: {str(e)}"
        )

@app.get("/reports")
async def list_reports():
    """List all available reports in Firebase Storage"""
    logger.info("Received request to list reports")
    try:
        result = firebase_manager.list_files()
        if result["status"] == "error":
            logger.error(f"Error listing reports: {result['message']}")
            raise HTTPException(status_code=500, detail=result["message"])
        logger.info("Successfully retrieved report list")
        return result
        
    except Exception as e:
        logger.error(f"Error listing reports: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing reports: {str(e)}"
        )

@app.post("/reports/fetch/{file_name}")
async def fetch_report(file_name: str, max_retries: int = 5, retry_delay: int = 2):
    """
    Fetch and process a report file with retries
    """
    try:
        # Clean up filename and ensure correct path
        file_name = file_name.replace('reports/', '')  # Remove if present
        if not file_name.endswith('.pdf'):
            file_name += '.pdf'
            
        # Construct Firebase path and txt filename
        firebase_path = f"reports/{file_name}"
        txt_filename = os.path.splitext(file_name)[0] + '.txt'  # Create txt filename
        
        logger.info(f"Attempting to fetch file: {firebase_path}")
        
        # Use Firebase manager to fetch the file
        result = firebase_manager.fetch_file(firebase_path)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=404,
                detail=result["message"]
            )
            
        local_path = Path(result["details"]["file_path"])
        
        # First convert PDF to text using PDFConverter
        logger.info(f"Converting PDF to text: {local_path}")
        text_result = pdf_converter.process_pdf(str(local_path), txt_filename)
        
        if text_result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=text_result["message"]
            )
            
        # Then process PDF for tables
        logger.info(f"Processing PDF for tables: {local_path}")
        folder_name = os.path.splitext(file_name)[0]
        output_dir = STORAGE_DIR / "table_outputs" / folder_name
        os.makedirs(output_dir, exist_ok=True)
        
        table_result = process_pdf(str(local_path), str(output_dir))
        
        # Extract and analyze text content - use txt_filename without .pdf extension
        logger.info(f"Extracting text content from: {txt_filename}")
        text_analysis = await extract_report_text(txt_filename)  # Pass the .txt filename
        
        return {
            "status": "success",
            "message": f"File {file_name} downloaded and processed successfully",
            "file_path": str(local_path),
            "text_result": text_result,
            "table_result": table_result,
            "text_analysis": text_analysis
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing file {file_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@app.post("/reports/extract/text/{report_name}")
async def extract_report_text(report_name: str):
    """Extract and analyze text content of a processed report"""
    logger.info(f"Received request to extract text from report: {report_name}")
    try:
        # Ensure the filename ends with .txt
        if not report_name.endswith('.txt'):
            report_name = os.path.splitext(report_name)[0] + '.txt'
        
        # Extract company name from filename
        parts = report_name.split('_')
        if len(parts) >= 3 and parts[0].isdigit():
            # Format: YYYYMMDD_HHMMSS_company.txt
            company_name = '_'.join(parts[2:]).replace('.txt', '')
        else:
            # Format: company.txt
            company_name = report_name.replace('.txt', '')
            
        company_name = company_name.upper()  # Convert to uppercase for consistency
        
        # Get database connection from pool
        conn = db_pool.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if company exists and get CompanyID
            cursor.execute(
                "SELECT CompanyID FROM company_info WHERE UPPER(CompanyName) = %s",
                (company_name,)
            )
            result = cursor.fetchone()
            
            if not result:
                # Company doesn't exist, insert it
                cursor.execute(
                    """INSERT INTO company_info 
                       (CompanyName, Sector, Location, FoundedYear, Website) 
                       VALUES (%s, 'Technology', 'Unknown', NULL, NULL)""",
                    (company_name,)
                )
                company_id = cursor.lastrowid
            else:
                company_id = result[0]

            # Analyze the report
            txt_path = STORAGE_DIR / "txt_outputs" / f"{report_name}"
            if not txt_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"Text file for '{report_name}' not found. Please process the PDF first."
                )
            
            result = report_analyzer.analyze_report(str(txt_path))
            
            if result["status"] == "error":
                raise HTTPException(
                    status_code=500,
                    detail=result["message"]
                )

            # Extract report year from the content or filename
            analysis = result["analysis"]
            report_year = analysis.get('report_year')
            
            # If report_year is not found in analysis, try to extract from filename
            if not report_year:
                # Extract year from filename (assuming format: YYYYMMDD_HHMMSS_company.txt)
                try:
                    report_year = int(report_name.split('_')[0][:4])
                except:
                    report_year = 2023  # Default to current year if extraction fails
            
            # Store report_year back in analysis dict
            analysis['report_year'] = report_year

            # Update governance table
            cert_count = len(analysis.get('iso_certificates', []))
            cursor.execute("""
                INSERT INTO governance 
                (CompanyID, ReportYear, BoardComposition, EthicalBehaviour, RiskManagement, CertificationList)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                BoardComposition = VALUES(BoardComposition),
                EthicalBehaviour = VALUES(EthicalBehaviour),
                RiskManagement = VALUES(RiskManagement),
                CertificationList = VALUES(CertificationList)
            """, (
                company_id,
                report_year,  # Use report_year directly
                1 if analysis.get('board_diversity', 0) > 0 else 0,
                1 if analysis.get('ethical_corruption', 0) > 0 else 0,
                1 if analysis.get('risk_management', 0) > 0 else 0,
                cert_count
            ))

            # Update social table
            cursor.execute("""
                INSERT INTO social 
                (CompanyID, ReportYear, DataSecurity, CustomerPrivacy, Cybersecurity, 
                 GenderStats, AgeStats, EmployeeCount, MalePercentage, FemalePercentage, 
                 TrainingHours, WorkRelatedInjuries)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, NULL, NULL, NULL, NULL)
                ON DUPLICATE KEY UPDATE
                DataSecurity = VALUES(DataSecurity),
                CustomerPrivacy = VALUES(CustomerPrivacy),
                Cybersecurity = VALUES(Cybersecurity),
                GenderStats = VALUES(GenderStats),
                AgeStats = VALUES(AgeStats)
            """, (
                company_id,
                report_year,  # Use report_year directly instead of analysis['report_year']
                1 if analysis.get('data_security', 0) > 0 else 0,
                1 if analysis.get('customer_privacy', 0) > 0 else 0,
                1 if analysis.get('cybersecurity', 0) > 0 else 0,
                1 if analysis.get('gender_diversity', 0) > 0 else 0,
                1 if analysis.get('age_diversity', 0) > 0 else 0
            ))
            
            conn.commit()
            
            return {
                "status": "success",
                "report_name": report_name,
                "company_id": company_id,
                "analysis": analysis,  # This now includes the report_year
                "database_update": {
                    "company": company_name,
                    "report_year": report_year,  # Use report_year directly
                    "governance_updated": True,
                    "social_updated": True
                }
            }

        finally:
            cursor.close()
            conn.close()
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error extracting text: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting text: {str(e)}"
        )

@app.post("/reports/extract/table/{report_name}")
async def extract_report_tables(report_name: str):
    """Extract and analyze table content from a processed report"""
    logger.info(f"Received request to extract tables from report: {report_name}")
    try:
        # Clean up filename and ensure correct path
        report_name = report_name.replace('reports/', '')  # Remove if present
        if report_name.endswith('.pdf'):
            report_name = report_name[:-4]  # Remove .pdf extension
        if report_name.endswith('.txt'):
            report_name = report_name[:-4]  # Remove .txt extension
            
        # Extract company name from filename
        company_name = '_'.join(report_name.split('_')[2:])
        company_name = company_name.upper()
        
        # Process tables from the correct directory
        table_dir = STORAGE_DIR / "table_outputs" / report_name
        if not table_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Table directory not found: {table_dir}. Please process the PDF first."
            )
        
        logger.info(f"Processing tables from directory: {table_dir}")
        table_result = table_extractor.process_tables(str(table_dir))
        
        if table_result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=table_result["message"]
            )

        # Get report year from table data or filename
        report_year = table_result.get("data", {}).get("ReportYear")
        if not report_year:
            try:
                report_year = int(report_name.split('_')[0][:4])
            except:
                report_year = 2023
        
        return {
            "status": "success",
            "report_name": report_name,
            "company_name": company_name,
            "table_analysis": table_result["data"],
            "report_year": report_year
        }
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error extracting tables: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting tables: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5106)