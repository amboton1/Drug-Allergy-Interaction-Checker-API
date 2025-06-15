#!/usr/bin/env python3

import sqlite3
import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Database connection
def get_db_connection():
    try:
        # Use absolute path to database
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../database/allergy_api.db'))
        logger.info(f"Connecting to database at: {db_path}")
        
        if not os.path.exists(db_path):
            logger.error(f"Database file not found at: {db_path}")
            raise FileNotFoundError(f"Database file not found at: {db_path}")
            
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        logger.info("Health check requested")
        conn = get_db_connection()
        result = conn.execute('SELECT 1').fetchone()
        conn.close()
        
        logger.info("Health check successful")
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'version': '1.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting minimal API server for troubleshooting")
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    except Exception as e:
        logger.critical(f"Failed to start server: {e}")
