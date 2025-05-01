import flask
from flask import request, render_template, redirect
from flask import Flask
import requests
from flask_cors import CORS
import base64
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
from backend.database.db_utils import execute_, update_query, insert_query

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


app = Flask("__name__")

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
                    from_email = msg["From"]
                    subject, encoding = decode_header(msg["subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoder or 'UTF-8')
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
                                    # folder = "ingested_emails"
                                    # os.makedirs(folder, exist_ok=True)
                                    # filepath = os.path.join(folder, filename)
                                    # with open(filepath, "wb") as f:
                                    #     f.write(part.get_payload(decode=True))
                                    # print(f"Saved email attachment: {filepath}")
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
    
@app.route("/get_ingested_invoices", methods=["GET", "POST"])
def get_ingested_invoices():
    data = request.get_json()
    logging.info(f"Request Data is {data}")
    try:
        database = "invoice_management"
        query = """
        SELECT invoice_id, ingested_time AS ingested_datetime, ingested_from AS from_email
        FROM `ingested_files`
        ORDER BY ingested_datetime;
        """
        result = execute_(query, database)
        message = "Query Executed Successfully!"
        logging.info("Query Executed Successfully!")
        return {
            "flag" : True,
            "message" : message
            "data" : result,
        }
    except Exception as e:
        logging.exception(f"Error occured with Exception {e}")
        message = "Internal Error Occured"
        return {
            "flag" : False,
            "message" : message
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
    app.run(debug=False, host="0.0.0.0", port=8081)