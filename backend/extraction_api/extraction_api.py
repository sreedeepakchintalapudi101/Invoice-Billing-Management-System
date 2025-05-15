import flask
from flask import request, render_template, redirect
from flask import Flask
import requests
from flask_cors import CORS
import base64
import re
# import APScheduler
import os
import email
import smtplib
import imaplib
import paramiko
import uuid
from email import message_from_bytes
from email.header import decode_header
import time
from datetime import datetime
import threading
from backend.database.db_utils import get_connection, execute_, update_query, insert_query
import cv2
import pytesseract
from PIL import Image

app = Flask(__name__)
CORS(app)

import logging
import dotenv
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    headers = [
        logging.StreamHandler(),
    ]
)

@app.route("/", methods=["GET", "POST"])
def home():
    message = "Successfully launched!"
    return {
        "flag" : True,
        "message" : message
    }
    
@app.route("/extraction_api", methods=["GET", "POST"])
def extraction_api():
    data = request.get_json()
    database = "extraction_management"
    logging.info(f"The request data is {data}")
    try:
        invoice_id = data.get("invoice_id", "")
        logging.info(f"The Invoice ID is {invoice_id}")
        grey_image_paths = data.get("grey_image_paths", "")
        logging.info(f"The grey image paths are {grey_image_paths}")
        # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not invoice_id or not grey_image_paths:
            message = "Invoice ID (or) Grey Image Paths are missing!"
            logging.info(f"The invoice_id (or) grey image paths are missing")
            return {
                "flag" : False,
                "message" : message
            }
            
        for grey_image_path in grey_image_paths:
            logging.info(f"The grey image path is {grey_image_path}")
            if not os.path.exists(grey_image_path):
                logging.debug(f"The image does not exist with path {grey_image_path}")
                continue
            logging.info(f"The current grey image path is {grey_image_path}")
            ocr_text = pytesseract.image_to_string(Image.open(grey_image_path))
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            check_query = f"""
                SELECT `invoice_id` FROM `raw_ocr`
                WHERE `invoice_id` = %s AND `image_path` = %s;
            """
            params = [invoice_id, grey_image_path]
            result = execute_(database, check_query, params)
            
            if result:
                update_query_sql = """
                    UPDATE `raw_ocr`
                    SET `raw_text` = %s, `updated_at` = %s
                    WHERE `invoice_id` = %s AND `image_path` = %s;
                """
                update_params = [ocr_text, current_time, invoice_id, grey_image_path]
                update_query(database, update_query_sql, update_params)
                logging.info(f"Updated OCR data for {grey_image_path}")
            else:
                insert_query_sql = """
                    INSERT INTO `raw_ocr`
                    (`invoice_id`, `image_path`, `raw_text`, `created_at`, `updated_at`)
                    VALUES (%s, %s, %s, %s, %s);
                """
                insert_params = [invoice_id, grey_image_path, ocr_text, current_time, current_time]
                insert_query(database, insert_query_sql, insert_params)
                logging.info(f"Inserted OCR data for {grey_image_path}")
                
        message = "Data extraction successful"
        return {
            "flag" : True,
            "message" : message,
            "invoice_id" : invoice_id
        }
    except Exception as e:
        logging.error(f"Error occured with exception {e}")
        message = "Something went wrong in Data Extraction"
        return {
            "flag" : False,
            "message" : message
        }
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8086)