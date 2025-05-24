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
import json
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
        logging.StreamHandler()
    ]
)

@app.route("/", methods=["GET", "POST"])
def home():
    message = "Successfully Launched!"
    return {
        "flag" : True,
        "message" : message
    }
    
@app.route("/ocr_postprocessing_api", methods=["GET","POST"])
def ocr_postprocessing_api():
    database = "extraction_management"
    try:
        data = request.get_json()
        logging.info(f"The request data is {data}")
        invoice_id = data.get("invoice_id", "")
        logging.info(f"The invoice id is {invoice_id}")
        update_flag = data.get("update_flag", "")
        logging.info(f"The Update Flag is {update_flag}")
        if not update_flag:
            logging.info(f"Update Flag missing!")
            message = "Updated flag missing!"
            return {
                "flag" : False,
                "message" : message
            }
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"The current time is {current_time}")
        select_query = """
        SELECT * FROM `raw_ocr`
        WHERE invoice_id = %s;
        """
        params = [invoice_id]
        select_result = execute_(database, select_query, params)
        logging.info(f"The result is {select_result}")
        ocr_dict = json.loads(select_result[0]["extracted_text"])
        logging.info(f"The ocr dict is {ocr_dict}")
        processed_dict = {}
        logging.info(f"The processed dict is {processed_dict}")
        template_type = ""
        for item in ocr_dict["extracted"][0]["ocr_data"]:
            if item["label"] == "plain text":
                if 1600 < item["bbox"][0] < 1900 and 550 < item["bbox"][1] < 570 and 3050 < item["bbox"][2] < 3100 and 1000 < item["bbox"][3] < 1100:
                    raw_text = item["text"]
                    logging.info(f"The raw text is {raw_text}")
                    lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip() ]
                    logging.info(f"The lines at billing address are {lines}")
                    billing_address_lines = []
                    for line in lines:
                        if "Amazon.in" in line or "amazon" in line.lower() or "amazon" in line:
                            template_type = "Amazon"
                        elif "Billing Address" in line:
                            continue
                        elif "State/UT Code" in line:
                            match = re.search(r"^State/UT Code:\s*(\d+)$", line)
                            processed_dict["State/UT Code"] = match.group(1)
                        else:
                            billing_address_lines.append(line)
                    processed_dict["Billing Address"] = ",".join(billing_address_lines)
                    logging.info(f"The Processed dict at billing address is {processed_dict}")
                elif 1600 < item["bbox"][0] < 1800 and 1100 < item["bbox"][1] < 1300 and 3000 < item["bbox"][2] < 3100 and 1800 < item["bbox"][3] < 2300:
                    raw_text = item["text"]
                    lines = [line.strip() for line in item["text"].split("\n") if line.strip()]
                    logging.info(f"The lines at shipping address are {lines}")
                    shipping_address_lines = []
                    for line in lines:
                        if "Shipping Address" in line:
                            logging.info(f"The Shipping Address Line is {line}")
                            start_index = 0
                            end_index = -1
                            for i, line in enumerate(lines):
                                if "Shipping Address" in line:
                                    start_index += i + 1
                                if "State/UT Code" in line:
                                    end_index = i
                            if start_index != -1 and end_index != -1:
                                shipping_address_lines.extend(lines[start_index:end_index])
                            logging.info(f"The Shipping Address lines are {shipping_address_lines}")
                            processed_dict["Shipping Address"] = " ".join(shipping_address_lines)
                            logging.info(f"The processed dict at shipping address is {processed_dict['Shipping Address']}")
                        elif "State/UT Code" in line:
                            match = re.search(r"^State/UT Code:\s*(\d+)$", line)
                            if match:
                                processed_dict["State/UT Code"] = match.group(0)[-2:]
                        elif "Place of supply" in line:
                            match = re.search(r"^Place of supply:\s*(.+)$", line)
                            if match:
                                processed_dict["Place of supply"] = match.group(0)[match.group(0).index(":") + 2:]
                                logging.info(f"The processed_dict at place of supply is {processed_dict['Place of supply']}")    
                                if not processed_dict["Place of supply"].startswith("A"):
                                    processed_dict["Place of supply"] = "A" + processed_dict["Place of supply"]
                                    logging.info(f"The processed_dict at place of supply without A is {processed_dict['Place of supply']}")
                        elif "Place of delivery" in line:
                            match = re.search(r"^Place of delivery[:;]\s*(.+)$", line)
                            logging.info(f"The match is {match}")
                            if match:
                                value_list = match.group(1).split()
                                logging.info(f"The Value is {value_list}")
                                place = " ".join(value_list)
                                if not place.startswith("A"):
                                    place = "A" + place
                                processed_dict["Place of delivery"] = place
                                logging.info(f"The processed dict after Place of delivery is {processed_dict['Place of delivery']}")
                        elif "Invoice Number" in line:
                            match = re.search(r"^Invoice Number\s*:\s*(.+)$", line)
                            logging.info(f"The Match is {match}")
                            logging.info(f"The Group 0 is {match.group(0)}")
                            logging.info(f"The Group 1 is {match.group(1)}")
                            if match:
                                processed_dict["Invoice Number"] = match.group(1)
                                logging.info(f"The processed dict at Invoice Number is {processed_dict['Invoice Number']}")
                        elif "Invoice Details" in line:
                            match = re.search(r"^Invoice Details\s*:\s*(.+)$", line)
                            logging.info(f"The Match is {match}")
                            logging.info(f"The Group 0 is {match.group(0)}")
                            logging.info(f"The Group 1 is {match.group(1)}")
                            if match:
                                processed_dict["Invoice Details"] = match.group(1)
                                logging.info(f"The processed dict at Invoice Details is {processed_dict['Invoice Details']}")
                        elif "Invoice Date" in line:
                            logging.info(line)
                            match = re.search(r"^Invoice Date\s*:\s*(\d.+)$", line)
                            logging.info(f"The Match is {match}")
                            logging.info(f"The Group 0 is {match.group(0)}")
                            logging.info(f"The Group 1 is {match.group(1)}")
                            if match:
                                processed_dict["Invoice Date"] = match.group(0)[match.group(0).index(":") + 2:]
                                logging.info(f"The processed dict at Invoice Date is {processed_dict['Invoice Date']}")
                    processed_dict["Billing Address"] = " ".join(shipping_address_lines)
                    logging.info(f"The processed dict at Billing Address is {processed_dict['Billing Address']}")
                elif 1800 < item["bbox"][0] < 2200 and 2100 < item["bbox"][1] < 2300 and 3000 < item["bbox"][2] < 3200 and 2300 < item["bbox"][3] < 2500:
                    raw_text = item["text"]
                    lines = [line.strip() for line in item["text"].split("\n") if line.strip()]
                    for line in lines:
                        if "Invoice Number" in line:
                            match = re.search(r"^Invoice Number\s*:\s*(.+)$", line)
                            logging.info(f"The Match is {match}")
                            logging.info(f"The Group 0 is {match.group(0)}")
                            logging.info(f"The Group 1 is {match.group(1)}")
                            logging.info(f"The match for Invoice Number is {match}")
                            if match:
                                processed_dict["Invoice Number"] = match.group(1)
                                logging.info(f"The Processed dict after Invoice Number is {processed_dict['Invoice Number']}")
                        elif "Invoice Details" in line:
                            match = re.search(r"^Invoice Details\s*:\s*(.+)$", line)
                            logging.info(f"The Match is {match}")
                            logging.info(f"The Group 0 is {match.group(0)}")
                            logging.info(f"The Group 1 is {match.group(1)}")
                            if match:
                                processed_dict["Invoice Details"] = match.group(1)
                                logging.info(f"The Processed Dict after Invoice Details are {processed_dict['Invoice Details']}")
                        elif "Invoice Date" in line:
                            match = re.search(r"^Invoice Date\s*:\s*(\d.+)$", line)
                            logging.info(f"The Match is {match}")
                            logging.info(f"The Group 0 is {match.group(0)}")
                            logging.info(f"The Group 1 is {match.group(1)}")
                            if match:
                                processed_dict["Invoice Date"] = match.group(1)
                                logging.info(f"The processed dict at Invoice Date is {processed_dict['Invoice Date']}")
                elif 200 < item["bbox"][0] < 300 and 500 < item["bbox"][1] < 600 and 1000 < item["bbox"][2] < 1600 and 900 < item["bbox"][3] < 1100:
                    raw_text = item["text"]
                    lines = [line.strip() for line in item["text"].split("\n") if line.strip()]
                    logginng.info(f"the lines are {lines}")
                    result_string = ""
                    logging.info(f"The result string is {result_string}")
                    for line in lines:
                        if "Sold By" in line:
                            logging.info(f"The Sold By line is {line}")
                            continue
                        else:
                            result_string += line + " "
                            logging.info(f"The current line is {line}")
                            logging.info(f"The result string is {result_string.strip()}")
                    processed_dict["Sold By"] = result_string.strip()
                elif 200 < item["bbox"][0] < 300 and 1000 < item["bbox"] < 1200 and 1300 < item["bbox"] < 1500 and 1200 < item["bbox"] < 1400:
                    raw_text = item["text"]
                    logging.info(f"The raw text is {raw_text}")
                    lines = [line.strip() for line in item["text"].split("\n") if line.strip()]
                    logging.info(f"The lines are {lines}")
                    for line in lines:
                        logging.info(f"The line is {line}")
                        if "PAN No" in line:
                            logging.info(f"The current line is {line}")
                            match = re.search(r"^PAN No:\s*(.+)$")
                            logging.info(f"The Match is {match}")
                            logging.info(f"The Group 0 is {match.group(0)}")
                            logging.info(f"The Group 1 is {match.group(1)}")
                            if match:
                                processed_dict["PAN No"] = match.group(1)
                                logging.info(f"The processed dict of PAN No is {processed_dict['PAN No']}")
                        if "GST Registration No" in line:
                            logging.info(f"The current line is {line}")
                            match = re.search(r"^GST Registration No:\s*(.+)$")
                            logging.info(f"The Match is {match}")
                            logging.info(f"The Group 0 is {match.group(0)}")
                            logging.info(f"The Group 1 is {match.group(1)}")
                            if match:
                                processed_dict["GST Registration No"] = match.group(1)
                                logging.info(f"The processed dict of GST Registration No is {processed_dict['GST Registration No']}")
                elif 200 < item["bbox"][0] < 300 and 1900 < item["bbox"][0] < 2300 and 1200 < item["bbox"][1] < 1400 and 2050 < item["bbox"] < 2450:
                    raw_text = item["text"]
                    logging.info(f"The raw text is {raw_text}")
                    lines = [item.strip() for item in raw_text.split("\n") if item.strip()]
                    logging.info(f"The lines are {lines}")
                    for line in lines:
                        if "Order Number" in line:
                            logging.info(f"The current line is {line}")
                            match = re.search(r"^Order Number:\s*(.+)$")
                            logging.info(f"The Match is {match}")
                            logging.info(f"The Group 0 is {match.group(0)}")
                            logging.info(f"The Group 1 is {match.group(1)}")
                            if match:
                                processed_dict["Order Number"] = match.group(1)
                                logging.info(f"The processed dict of Order Number is {processed_dict["Order Number"]}")
                        if "Order Date" in line:
                            logging.info(f"The current line is {line}")
                            match = re.search(r"^Order Date:\s*(.+)$")
                            logging.info(f"The Match is {match}")
                            logging.info(f"The Group 0 is {match.group(0)}")
                            logging.info(f"The Group 1 is {match.group(1)}")
                            if match:
                                processed_dict["Order Date"] = match.group(1)
                                logging.info(f"The processed dict of Order Data is {processed_dict["Order Date"]}")
        logging.info(f"The processed_dict is {processed_dict}")
        if update_flag == "new":
            insertion_query = f"""
            INSERT INTO `ocr_info`
            (`invoice_id`, `ocr_dict`, `created_at`, `updated_at`, `template`)
            VALUES
            (%s, %s, %s, %s, %s);
            """
            params = [invoice_id, json.dumps(processed_dict), current_time, current_time, template_type]
            insertion_result = insert_query(database, insertion_query, params)
            logging.info(f"The insertion result is {insertion_result}")
            if insertion_result:
                message = "Data inserted successfully!"
                return {
                    "flag" : True,
                    "invoice_id" : invoice_id,
                    "message" : message,
                    "extracted_dict" : processed_dict
                }
        elif update_flag == "update":
            updation_query = """
            UPDATE `ocr_info`
            SET `ocr_dict` = %s, `updated_at` = %s, `Template` = %s
            WHERE `invoice_id` = %s;
            """
            params = [json.loads(processed_dict), current_time, template_type, invoice_id]
            updation_result = update_query(database, updation_query, params)
            logging.info(f"The updation result is {updation_result}")
            if updation_result:
                message = "Data updated successfully!"
                return {
                    "flag" : True,
                    "invoice_id" : invoice_id,
                    "message" : message,
                    "extracted_dict" : processed_dict
                }
        else:
            logging.info(f"The insert (or) update operation failed")
            message = "Insertion/Updation failed"
            return {
                "flag" : False,
                "message" : message,
                "extracted_dict" : {}
            }
    except Exception as e:
        message = "Something went wrong!"
        logging.info(f"Error occured with Exception {e}")
        return {
            "flag" : False,
            "message" : message
        }
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8087)