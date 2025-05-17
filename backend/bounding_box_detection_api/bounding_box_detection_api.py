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
import ultralytics
from huggingface_hub import hf_hub_download
from doclayout_yolo import YOLOv10

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level = logging.DEBUG,
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

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8088)