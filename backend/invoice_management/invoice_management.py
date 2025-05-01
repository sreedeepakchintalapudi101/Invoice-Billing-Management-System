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
    headers=[
        logging.StreamHandler()
    ]
)

@app.route("/", methods=["GET","POST"])
def home():
    return {
        "flag" : True,
        "message" : "Successfully Launched"
    }

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
