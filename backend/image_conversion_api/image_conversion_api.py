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
app = Flask(__name__)
CORS(app)

import logging
import dotenv
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

@app.route("/", methods=["GET", "POST"])
def home():
    message = "Successfully Launched!"
    return {
        "flag": True,
        "message": message
    }

def image_preprocess(image_path, output_path, scale_factor=2.0):
    try:
        logging.info(f"The File Path is {image_path}")
        image = cv2.imread(image_path)
        logging.info(f"The image is {image}")
        height, width, channels = image.shape
        image = cv2.resize(image, (int(width * scale_factor), int(height * scale_factor)), interpolation=cv2.INTER_CUBIC)
        logging.info(f"The Resized Image Shape is {image.shape}")
        base_name = image_path.split(".")[0]
        logging.info(f"The Base Name is {base_name}")
        grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        bi_lateral_blurred_image = cv2.bilateralFilter(grey_image, 9, 75, 75)
        threshold_image = cv2.adaptiveThreshold(bi_lateral_blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        morphological_image = cv2.morphologyEx(threshold_image, cv2.MORPH_OPEN, kernel, iterations=1)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        morphological_image_final = cv2.morphologyEx(morphological_image, cv2.MORPH_CLOSE, kernel, iterations=1)
        morphological_image_final_path = os.path.join(output_path, f"{base_name}_final_image.jpg")
        cv2.imwrite(morphological_image_final_path, morphological_image_final)
        logging.info(f"The grey image is saved in {morphological_image_final_path}")
        return morphological_image_final_path
    except Exception as e:
        logging.error(f"Error occured with Exception {e}")
        return None
        
@app.route("/convert_image", methods=["GET", "POST"])
def convert_image():
    data = request.get_json()
    logging.info(f"Request Data is {data}")
    invoice_id = data.get("invoice_id","")
    logging.info(f"Invoice ID is {invoice_id}")
    file_name = data.get("filename","")
    logging.info(f"File name is {file_name}")
    try:
        if not invoice_id or not file_name:
            message = {"Invoice ID (or) File Name is Missing"}
            return {
                "flag" : False,
                "message" : message
            }
        file_path = os.path.join("/app/ingested_files", invoice_id)
        logging.info(f"The file path is {file_path}")
        if not os.path.exists(file_path):
            message = "File does not exists in given path"
            return {
                "flag" : False,
                "message" : message
            }
        image_files = []
        for image in os.listdir(file_path):
            # if image.endswith(".jpeg") or image.endswith("jpeg") or image.endswith("png"):
            if image.lower().endswith((".jpg", ".jpeg", ".png")):
                image_files.append(image)
        if not image_files:
            logging.info(f"Image file does not exists")
            message = "File Not Found!"
            return {
                "flag" : False,
                "message" : message
            }
        grey_image_paths = []
        for index, image_file in enumerate(image_files):
            image_path = os.path.join(file_path, image_file)
            logging.info(f"The Image Path is {image_path}")
            output_path = os.path.join("/app/ingested_files", invoice_id)
            grey_image = image_preprocess(image_path, output_path)
            if grey_image:
                grey_image_paths.append(grey_image)
        # message = "The Files are successfully Preprocessed"
        # return {
        #     "flag" : True,
        #     "message" : message, 
        #     "processed_images" : grey_image_paths
        # }
        if not grey_image_paths:
            message = "Image Preprocessing Failed!"
            return {
                "flag" : False,
                "message" : message
            }
        try:
            extraction_api_url = "http://bounding_box_detection_api:8088/bounding_box_detection_api"
            extraction_api_params = {
                "invoice_id" : invoice_id,
                "grey_image_paths" : grey_image_paths
            }
            
            extraction_api_response = requests.post(extraction_api_url, json=extraction_api_params)
            logging.info(f"The extraction_api response is {extraction_api_response}")
            if extraction_api_response.status_code != 200:
                message = "extraction_api failed!"
                return {
                    "flag" : False,
                    "message" : message
                }
            final_result = extraction_api_response.json()
            flag = final_result.get("flag", False)
            message = final_result.get("message", "")
            extracted_data = final_result.get("extracted_data", "")
            
            return {
                "flag" : flag,
                "message" : message,
                "processed_files" : grey_image_paths,
                "extracted_data" : extracted_data
            }
        except Exception as e:
            logging.error(f"Error occured with Exception {e}")
            message = "Something went Wrong!"
            return {
                "flag" : False,
                "message" : message
            }
    except Exception as e:
        logging.error(f"Error occured with Exception {e}")
        message = "Internal Error Occured"
        return {
            "flag" : False,
            "message" : message
        }
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8085)