from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import pandas as pd
from pathlib import Path
import os
from scripts.db_connect import get_connection_pool, fetch_environmental_data, fetch_social_data, fetch_governance_data, fetch_ESG_data, fetch_predict_data, fetch_company_info, update_table, update_predict_table
from scripts.esg_score import calculate_environmental_score, calculate_social_score, calculate_governance_score, decimal_to_float, ESG_WEIGHTS
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
from scripts.esg_financial import update_financial_metrics
from datetime import datetime
from scripts.env_commentary import analyze_env_metrics

# pip install fastapi
# pip install uvicorn
# pip install pandas
# pip install numpy
# pip install statsmodels

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events manager for FastAPI"""
    # Startup
    logger.info("Server starting up - running initial predictions")
    try:
        # Fetch ESG data and generate predictions
        esg_score = fetch_ESG_data(db_pool)
        predictions_df = generate_predictions(esg_score)
        update_predict_table(db_pool, predictions_df)
        logger.info("Initial predictions completed successfully")
    except Exception as e:
        logger.error(f"Error during startup predictions: {str(e)}")
        # We log the error but don't raise it to allow the server to start
    
    yield  # Server is running
    
    # Shutdown
    logger.info("Server shutting down")
    
# Update FastAPI initialization to use lifespan
app = FastAPI(lifespan=lifespan)

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


@app.post("/api/financial/update")
async def update_financial_data():
    """Update financial metrics and correlations"""
    try:
        result = await update_financial_metrics(db_pool)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error updating financial data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating financial data: {str(e)}"
        )


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
        
        # Calculate scores - properly unpack the tuple
        environmental_percentile, env_component_scores = calculate_environmental_score(env_data, pax)
        social_score = calculate_social_score(social_data)
        governance_score = calculate_governance_score(gov_data)
        
        # Create ESG score DataFrame
        esg_score = pd.DataFrame({
            'CompanyID': env_data['CompanyID'],
            'ReportYear': env_data['ReportYear'],
            'Environmental_Score': environmental_percentile,
            'Social_Score': social_score,
            'Governance_Score': governance_score
        })
        
        # Process ESG scores
        esg_score = esg_score.fillna(0)
        for col in ['Environmental_Score', 'Social_Score', 'Governance_Score']:
            esg_score[col] = esg_score[col].clip(0, 10)
        
        # Calculate final ESG score with weights
        esg_score['Final_ESG_score'] = (
            esg_score['Environmental_Score'] * ESG_WEIGHTS['Environmental'] +
            esg_score['Social_Score'] * ESG_WEIGHTS['Social'] +
            esg_score['Governance_Score'] * ESG_WEIGHTS['Governance']
        )
        esg_score['Final_ESG_score'] = esg_score['Final_ESG_score'].clip(0, 10)
        
        # Update tables
        update_table(db_pool, env_component_scores, 'env_score')
        update_table(db_pool, esg_score, 'esg_scores')
        
        return {"message": "ESG scores calculated and updated successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

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
        base_name = os.path.splitext(file_name)[0]
        
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
        
        # Extract and analyze text content
        logger.info(f"Extracting text content from: {txt_filename}")
        text_analysis = await extract_report_text(txt_filename)
        
        # Update database with extracted data
        logger.info(f"Updating database with extracted data")
        update_result = await update_report_data(base_name)
        
        # Fetch updated ESG data
        logger.info("Fetching updated ESG data for predictions")
        esg_data = fetch_ESG_data(db_pool)
        
        # Generate new predictions
        logger.info("Generating new predictions")
        predictions_df = generate_predictions(esg_data)
        
        # Update predictions in database
        logger.info("Updating predictions in database")
        update_predict_table(db_pool, predictions_df)
        
        return {
            "status": "success",
            "message": f"File {file_name} processed and database updated successfully",
            "file_path": str(local_path),
            "processing_results": {
                "text_result": text_result,
                "table_result": table_result,
                "text_analysis": text_analysis
            },
            "database_updates": {
                "data_update": update_result,
                "predictions_updated": True
            }
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
        # Clean up filename
        report_name = report_name.replace('reports/', '')
        base_name = report_name.replace('.pdf', '').replace('.txt', '')
        
        # Extract year and company from filename (YYYYMMDD_HHMMSS_company)
        parts = base_name.split('_')
        if len(parts) >= 3:
            report_year = int(parts[0][:4])
            company_name = '_'.join(parts[2:]).upper()
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename format. Expected: YYYYMMDD_HHMMSS_company"
            )
            
        # Ensure the text file exists
        txt_path = STORAGE_DIR / "txt_outputs" / f"{base_name}.txt"
        if not txt_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Text file for '{base_name}' not found. Please process the PDF first."
            )
        
        # Analyze the report
        result = report_analyzer.analyze_report(str(txt_path))
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )

        # Add report year to analysis
        analysis = result["analysis"]
        analysis['report_year'] = report_year
            
        return {
            "status": "success",
            "report_name": base_name,
            "company_name": company_name,
            "report_year": report_year,
            "analysis": analysis,
            "metrics_found": {
                "governance": {
                    "board_diversity": bool(analysis.get('board_diversity')),
                    "ethical_corruption": bool(analysis.get('ethical_corruption')),
                    "risk_management": bool(analysis.get('risk_management')),
                    "iso_certificates": len(analysis.get('iso_certificates', []))
                },
                "social": {
                    "data_security": bool(analysis.get('data_security')),
                    "customer_privacy": bool(analysis.get('customer_privacy')),
                    "cybersecurity": bool(analysis.get('cybersecurity')),
                    "gender_diversity": bool(analysis.get('gender_diversity')),
                    "age_diversity": bool(analysis.get('age_diversity'))
                }
            }
        }
            
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
        # Clean up filename
        report_name = report_name.replace('reports/', '')
        base_name = report_name.replace('.pdf', '').replace('.txt', '')
        
        # Extract company from filename (YYYYMMDD_HHMMSS_company)
        parts = base_name.split('_')
        if len(parts) >= 3:
            company_name = '_'.join(parts[2:]).upper()
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename format. Expected: YYYYMMDD_HHMMSS_company"
            )
            
        # Process tables from the correct directory
        table_dir = STORAGE_DIR / "table_outputs" / base_name
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

        # Get metrics and year from table data
        metrics = table_result["data"]["metrics"]
        report_year = metrics["ReportYear"]  # Use the year from table extraction
        
        return {
            "status": "success",
            "report_name": base_name,
            "company_name": company_name,
            "report_year": report_year,
            "table_analysis": {
                "metrics": metrics,
                "metrics_found": [k for k, v in metrics.items() if v is not None],
                "metrics_missing": [k for k, v in metrics.items() if v is None],
                "environmental_metrics": {
                    "energy": metrics.get("EnergyConsumption"),
                    "emissions": metrics.get("GHGEmissions"),
                    "water": metrics.get("WaterUsage"),
                    "waste": metrics.get("WasteGenerated"),
                    "renewable": metrics.get("RenewableEnergyUse")
                },
                "social_metrics": {
                    "employee_count": metrics.get("EmployeeCount")
                }
            }
        }
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error extracting tables: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting tables: {str(e)}"
        )
        
        
@app.post("/reports/extract/update/data/{report_name}")
async def update_report_data(report_name: str):
    """Update database with extracted data from both text and tables"""
    logger.info(f"Updating database with extracted data for report: {report_name}")
    try:
        # Get text and table analysis results
        text_result = await extract_report_text(report_name)
        table_result = await extract_report_tables(report_name)
        
        # Extract key information
        company_name = text_result["company_name"]
        text_year = text_result["report_year"]
        table_year = table_result["report_year"]
        
        # Use table year if available, otherwise fall back to text year
        report_year = table_year if table_year else text_year
        
        # Log if there's a year mismatch
        if text_year != table_year:
            logger.warning(
                f"Report year mismatch for {report_name}: "
                f"text_year={text_year}, table_year={table_year}. "
                f"Using table year: {report_year}"
            )
        
        text_data = text_result["analysis"]
        table_data = table_result["table_analysis"]["metrics"]

        # Get database connection
        conn = db_pool.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get or create company
            cursor.execute(
                "SELECT CompanyID FROM company_info WHERE UPPER(CompanyName) = %s",
                (company_name,)
            )
            result = cursor.fetchone()
            
            if not result:
                cursor.execute(
                    """INSERT INTO company_info 
                       (CompanyName, Sector, Location, FoundedYear, Website) 
                       VALUES (%s, 'Technology', 'NULL', NULL, NULL)""",
                    (company_name,)
                )
                company_id = cursor.lastrowid
            else:
                company_id = result[0]

            # Update governance table
            cert_count = len(text_data.get('iso_certificates', []))
            cursor.execute("""
                INSERT INTO governance 
                (CompanyID, ReportYear, BoardComposition, EthicalBehaviour, 
                 RiskManagement, CertificationList)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                BoardComposition = VALUES(BoardComposition),
                EthicalBehaviour = VALUES(EthicalBehaviour),
                RiskManagement = VALUES(RiskManagement),
                CertificationList = VALUES(CertificationList)
            """, (
                company_id,
                report_year,
                1 if text_data.get('board_diversity', 0) > 0 else 0,
                1 if text_data.get('ethical_corruption', 0) > 0 else 0,
                1 if text_data.get('risk_management', 0) > 0 else 0,
                cert_count
            ))

            # Update social table
            cursor.execute("""
                INSERT INTO social 
                (CompanyID, ReportYear, DataSecurity, CustomerPrivacy, Cybersecurity,
                 GenderStats, AgeStats, EmployeeCount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                DataSecurity = VALUES(DataSecurity),
                CustomerPrivacy = VALUES(CustomerPrivacy),
                Cybersecurity = VALUES(Cybersecurity),
                GenderStats = VALUES(GenderStats),
                AgeStats = VALUES(AgeStats),
                EmployeeCount = COALESCE(VALUES(EmployeeCount), EmployeeCount)
            """, (
                company_id,
                report_year,
                1 if text_data.get('data_security', 0) > 0 else 0,
                1 if text_data.get('customer_privacy', 0) > 0 else 0,
                1 if text_data.get('cybersecurity', 0) > 0 else 0,
                1 if text_data.get('gender_diversity', 0) > 0 else 0,
                1 if text_data.get('age_diversity', 0) > 0 else 0,
                table_data.get('EmployeeCount')
            ))

            # Update environment table
            cursor.execute("""
                INSERT INTO environment 
                (CompanyID, ReportYear, EnergyConsumption, GHGEmissions,
                 WaterUsage, WasteGenerated, RenewableEnergyUse)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                EnergyConsumption = VALUES(EnergyConsumption),
                GHGEmissions = VALUES(GHGEmissions),
                WaterUsage = VALUES(WaterUsage),
                WasteGenerated = VALUES(WasteGenerated),
                RenewableEnergyUse = VALUES(RenewableEnergyUse)
            """, (
                company_id,
                report_year,
                table_data.get('EnergyConsumption'),
                table_data.get('GHGEmissions'),
                table_data.get('WaterUsage'),
                table_data.get('WasteGenerated'),
                table_data.get('RenewableEnergyUse')
            ))

            conn.commit()

            # Calculate new ESG scores and predictions
            esg_calc_result = await calculate_esg()
            predict_result = await predict_esg()
            
            # Integrate ESG updates into the existing response structure
            return {
                "status": "success",
                "report_name": report_name,
                "company_name": company_name,
                "report_year": {
                    "used": report_year,
                    "from_text": text_year,
                    "from_table": table_year,
                    "mismatch": text_year != table_year
                },
                "extraction_results": {
                    "text": {
                        "found": bool(text_data),
                        "metrics": {
                            "governance": {
                                "board_diversity": bool(text_data.get('board_diversity')),
                                "ethical_corruption": bool(text_data.get('ethical_corruption')),
                                "risk_management": bool(text_data.get('risk_management')),
                                "iso_certificates": len(text_data.get('iso_certificates', []))
                            },
                            "social": {
                                "data_security": bool(text_data.get('data_security')),
                                "customer_privacy": bool(text_data.get('customer_privacy')),
                                "cybersecurity": bool(text_data.get('cybersecurity')),
                                "gender_diversity": bool(text_data.get('gender_diversity')),
                                "age_diversity": bool(text_data.get('age_diversity'))
                            }
                        }
                    },
                    "table": {
                        "found": bool(table_data),
                        "metrics": {
                            "environmental": {
                                "energy": table_data.get("EnergyConsumption"),
                                "emissions": table_data.get("GHGEmissions"),
                                "water": table_data.get("WaterUsage"),
                                "waste": table_data.get("WasteGenerated"),
                                "renewable": table_data.get("RenewableEnergyUse")
                            },
                            "social": {
                                "employee_count": table_data.get("EmployeeCount")
                            }
                        }
                    }
                },
                "database_update": {
                    "company_id": company_id,
                    "tables_updated": {
                        "governance": True,
                        "social": True,
                        "environment": True
                    }
                },
                "esg_updates": {
                    "status": "success",
                    "esg_calculation": esg_calc_result.get("message", "ESG scores updated"),
                    "predictions": predict_result.get("message", "Predictions updated"),
                    "calculation_time": datetime.now().isoformat()
                }
            }

        finally:
            cursor.close()
            conn.close()

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating report data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating report data: {str(e)}"
        )  
        
        
@app.delete("/company/delete/{company_name}")
async def delete_company_data(company_name: str):
    """Delete all records associated with a company from all tables"""
    logger.info(f"Attempting to delete all records for company: {company_name}")
    try:
        # Get database connection
        conn = db_pool.get_connection()
        try:
            cursor = conn.cursor()
            
            # First get the company ID
            cursor.execute(
                "SELECT CompanyID FROM company_info WHERE UPPER(CompanyName) = %s",
                (company_name.upper(),)
            )
            result = cursor.fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"Company '{company_name}' not found"
                )
                
            company_id = result[0]
            
            # Delete from all related tables
            tables = ['environment', 'social', 'governance', 'esg_scores', 'esg_predictions']
            deleted_counts = {}
            
            for table in tables:
                cursor.execute(f"""
                    DELETE FROM {table}
                    WHERE CompanyID = %s
                """, (company_id,))
                deleted_counts[table] = cursor.rowcount
            
            # Finally delete from company_info
            cursor.execute("""
                DELETE FROM company_info
                WHERE CompanyID = %s
            """, (company_id,))
            deleted_counts['company_info'] = cursor.rowcount
            
            conn.commit()
            
            return {
                "status": "success",
                "message": f"Successfully deleted all records for {company_name}",
                "company_id": company_id,
                "deleted_records": deleted_counts
            }
            
        finally:
            cursor.close()
            conn.close()
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting company data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting company data: {str(e)}"
        )

@app.get("/dashboard/env/analysis/{company_id}")
async def get_env_analysis(company_id: int):
    """Get environmental metrics analysis for a specific company"""
    try:
        analysis = analyze_env_metrics(company_id)
        return {
            "status": "success",
            "data": analysis
        }
    except Exception as e:
        logger.error(f"Error generating environmental analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating environmental analysis: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5106)