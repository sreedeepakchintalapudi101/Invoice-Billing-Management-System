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

# def upscale_image(image, scale_factor = 2.0):
#     width, height, channels = image.shape
#     logging.info(f"The width and height of image are {width} and {height}")
#     image = cv2.resize(image, ((height * scale_factor), (width * scale_factor)))
#     return image

def image_preprocess(image_path, output_path, scale_factor=2.0):
    try:
        logging.info(f"The File Path is {image_path}")
        image = cv2.imread(image_path)
        logging.info(f"The image is {image}")
        height, width, channels = image.shape
        image = cv2.resize(image, (int(height * scale_factor), int(width * scale_factor)), interpolation=cv2.INTER_CUBIC)
        logging.info(f"The Resized Image Shape is {image.shape}")
        base_name = image_path.split(".")[0]
        logging.info(f"The Base Name is {base_name}")
        grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        grey_image_path = os.path.join(output_path, f"{base_name}_grey.jpg")
        cv2.imwrite(grey_image, grey_image_path)
        logging.info(f"The grey image is saved in {grey_image_path}")
        return grey_image_path
    except Exception as e:
        logging.error(f"Error occured with Exception {e}")
        
@app.route("/extraction_api", methods=["GET", "POST"])
def extraction_api():
    data = request.get_json()
    logging.info(f"Request Data is {data}")
    invoice_id = data.get("invoice_id","")
    logging.info(f"Invoice ID is {invoice_id}")
    file_name = data.get("file_name","")
    logging.info(f"File name is {file_name}")
    try:
        if not invoice_id or not file_name:
            message = {"Invoice ID (or) File Name is Missing"}
            return {
                "flag" : False,
                "message" : message
            }
        file_path = os.path.join("app/ingested_files", invoice_id)
        logging.info(f"The file path is {file_path}")
        if not os.path.exists:
            message = "File does not exists in given path"
            return {
                "flag" : False,
                "message" : message
            }
        image_files = []
        for image in os.listdir(file_path):
            if image.endswith(".jpeg") or image.endswith("jpeg") or image.endswith("png"):
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
            output_path = "app/"
            grey_image = image_preprocess(input_path, output_path)
            if grey_image:
                grey_image_paths.append(grey_image)
        message = "The Files are successfully Preprocessed"
        return {
            "flag" : True,
            "message" : message, 
            "processed_images" : grey_image_paths
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