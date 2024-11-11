from flask import Flask, request, jsonify
from flask_cors import CORS
from esg_commentary import analyze_trend_with_template
from db_connect import get_connection_pool, fetch_predict_data, fetch_company_info
import pandas as pd
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a connection pool
db_pool = get_connection_pool()

@app.route('/dashboard/analysis', methods=['POST'])
def generate_commentary():
    # Log the entire request
    logger.info(f"Received request: {request}")
    logger.info(f"Request JSON: {request.json}")
    logger.info(f"Request headers: {request.headers}")

    if db_pool is None:
        return jsonify({"error": "Database connection pool is not available."}), 500

    data = request.json
    company_id = data.get('company_id')
    logger.info(f"Received company_id: {company_id}")

    if not company_id:
        return jsonify({"error": "Company ID is required."}), 400

    try:
        esg_scores_df = pd.DataFrame(fetch_predict_data(db_pool))
        company_info_df = pd.DataFrame(fetch_company_info(db_pool))

        commentary = analyze_trend_with_template(esg_scores_df, company_id, company_info_df)
        logger.info(f"Generated commentary for company_id {company_id}: {commentary[:100]}...")  # Log first 100 chars of commentary
        return jsonify({"company_id": company_id, "commentary": commentary})
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5106)
