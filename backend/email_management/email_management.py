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

app = Flask(__name__)
CORS(app)

import logging
import dotenv
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# scheduler = APScheduler()

@app.route("/")
def home():
    return {
        "flag" : True,
        "message" : "Successfully launched"
    }

email_address = os.getenv("email")
password = os.getenv("password")
host = os.getenv("host")
imap_server = os.getenv("imap_server")

@app.route("/email_ingestion", methods=["POST", "GET"])
def email_ingestion():
    logging.info(f"Going to the Email Ingestion")
    logging.info(f"The Email is {email_address}")
    logging.info(f"The password is {password}")
    logging.info(f"The Host is {host}")
    logging.info(f"The Imap Server is {imap_server}")
    database = "invoice_management"
    try:
        imap = imaplib.IMAP4_SSL(imap_server)
        imap.login(email_address, password)
        imap.select("inbox")
        status, messages = imap.search(None,'unseen')
        for eid in messages[0].split():
            res, msg = imap.fetch(eid, "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    msg = message_from_bytes(response[1])
                    from_email_raw = msg["From"]
                    from_email = extract_email_address(from_email_raw)
                    subject, encoding = decode_header(msg["subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or 'UTF-8')
                    logging.info(f"Email Subject:, {subject}")
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get("Content-Disposition"):
                                filename = part.get_filename()
                                if filename:
                                    logging.info(f"File Name is {filename}")
                                    invoice_id = f"INV{uuid.uuid4().hex[:16]}"
                                    folder = os.path.join("ingested_files", invoice_id, "pdf")
                                    os.makedirs(folder, exist_ok=True)
                                    file_path = os.path.join(folder, filename)
                                    logging.info(f"Current working directory: {os.getcwd()}")
                                    logging.info(f"The file path is {file_path}")
                                    with open(file_path, "wb") as f:
                                        f.write(part.get_payload(decode=True))
                                        logging.info(f"Saved Email attachment{invoice_id}")
                                    query = """
                                    INSERT INTO ingested_files
                                    (invoice_id, file_name, ingested_time, from_email)
                                    VALUES
                                    (%s, %s, %s, %s);
                                    """
                                    params=[invoice_id, filename, datetime.now(), from_email]
                                    result = insert_query(database, query, params)
                                    if result:
                                        try:
                                            # camunda_url = "http://localhost:8080/engine-rest/process-definition/key/email_ingestion_workflow/start"
                                            camunda_url = "http://camunda_api:8080/engine-rest/process-definition/key/email_ingestion_workflow/start"
                                            payload = {
                                                "variables" : {
                                                    "payload" : {
                                                        "value" : {
                                                            "invoice_id" : invoice_id,
                                                            "file_name" : filename,
                                                        },
                                                        "type" : "String"
                                                    }
                                                }
                                            }
                                            response = requests.post(camunda_url, json=payload)
                                            if response.status_code in [200, 201]:
                                                logging.info(f"Camunda Process started successfully for invoice {invoice_id}")
                                                return {
                                                    "flag": True,
                                                    "message": f"Email processed and file saved successfully with invoice ID {invoice_id}"
                                                }
                                            else:
                                                logging.error(f"Failed to start Camunda process for invoice {invoice_id}. Status code: {response.status_code}")
                                                return {
                                                    "flag": False,
                                                    "message": f"Failed to start Camunda process for invoice {invoice_id}. Status code: {response.status_code}"
                                                }
                                        except Exception as e:
                                            logging.exception(f"Error Occured with Exception {e}")
                                            return {
                                                "flag": False,
                                                "message": f"Error Occured with Exception {e}"
                                            }
        imap.logout()
        return True
    
    except Exception as e:
        logging.exception(f"Error Occured with Exception {e}")
        return False

def basic_scheduler(interval_seconds):
    while True:
        email_ingestion()
        time.sleep(interval_seconds)

# def start_scheduler():
#     scheduler.add_job(func=email+email_ingestion, trigger="interval", seconds=2)
#     scheduler.start()
    
def start_scheduler():
    interval = 2
    scheduler_thread = threading.Thread(target=basic_scheduler, args=(interval,))
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
def extract_email_address(raw_email):
    match = re.search(r'<(.+?)>', raw_email)
    if match:
        return match.group(1)
    return raw_email.strip()

@app.route("/get_ingested_invoices", methods=["GET", "POST"])
def get_ingested_invoices():
    database = "invoice_management"
    try:
        data = request.get_json()  # Safely handles absence of JSON
        logging.info(f"Request Data is {data}")

        query = """
        SELECT invoice_id, ingested_time AS ingested_datetime, from_email AS ingested_from, file_name
        FROM ingested_files
        ORDER BY ingested_datetime;
        """
        
        try:
            result = execute_(database, query)
        except Exception as db_err:
            logging.exception(f"Database query failed: {db_err}")
            return {
                "flag": False,
                "message": f"Database query error: {str(db_err)}"
            }
        
        if not result:
            logging.warning("Query executed but returned no results.")
            return {
                "flag": False,
                "message": "No records found."
            }

        logging.info("Query Executed Successfully!")
        return {
            "flag": True,
            "message": "Query executed successfully!",
            "data": result
        }

    except Exception as e:
        logging.exception(f"Unhandled error occurred: {e}")
        return {
            "flag": False,
            "message": f"Unhandled error occurred: {str(e)}"
        }
        
@app.route("/download/<invoice_id>/<filename>", methods=["GET", "POST"])
def download_invoice(invoice_id, filename):
    try:
        file_path = os.path.join("ingested_files", invoice_id, "pdf", filename)
        if not os.path.isfile(file_path):
            message = f"The file donot exists with the filename {filename}"
            return {
                "flag" : False,
                "message" : message
            }
        else:
            blob_data = convert_to_blob(file_path)
            message = "Successfully converted to the Blob Data."
            return {
                "flag" : True,
                "message" : message,
                "blob_data" : blob_data,
                "filename" : filename 
            }
    except:
        logging.exception(f"Error occured with Exception {e}")
        message = "Something Went Wrong!"
        return {
            "flag" : False,
            "message" : message
        }
        
def convert_to_blob(file_path):
    logging.info(f"The File Path is {file_path}")
    with open(file_path, "rb") as file:
        file_data = file.read()
        blob_data = base64.b64encode(file_data).decode("UTF-8")
    return blob_data

if __name__ == "__main__":
    start_scheduler()
    app.run(debug=False, host="0.0.0.0", port=8083)