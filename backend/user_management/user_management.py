import flask
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import sqlite3
import re
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jinja2
import os
from dotenv import load_dotenv
from jinja2 import Template
import random, string
from datetime import datetime, timedelta
import ast
from ast import literal_eval
import bcrypt
import hashlib

load_dotenv()
email = os.getenv("email")
password = os.getenv("password")

from backend.database.db_utils import get_connection, execute_, update_query, insert_query
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def encrypt_password(password):
    salt = bcrypt.gensalt()
    password_bytes = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(
        password_bytes
        salt
    )
    return hashed_password

def validate_password(password):
    pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{8,}$')
    return bool(pattern.match(password))

@app.route("/")
def home():
    return {
        "flag" : True,
        "message" : "Successfully launched"
    }
    
def generate_otp():
    otp = ''.join(random.choices(string.digits, k=6))
    return otp

def fetch_email_body():
    database = "email_management"
    query = """
    select info from `email_templates` where type=%s;
    """
    params = ["OTP"]
    result = execute_(database, query, params)
    logging.info(f"The Result is {result}")
    return result

def send_email(to_email, subject, body):
    sender_email = email
    sender_password = password
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email
    
    part = MIMEText(body, "html")
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())

@app.route("/register_user", methods=["GET", "POST"])
def register_user():
    database = "user_management"
    if request.method == "POST":
        data = request.get_json()
        logging.info(f"The request data is {data}")
        email = data.get("email")
        logging.info(f"The Email is {email}")
        username = data.get("username")
        logging.info(f"The username is {username}")
        password = data.get("password")
        logging.info(f"The password is {password}")
        confirm_password = data.get("confirm_password")
        logging.info(f"The confirmed password is {confirm_password}")
        user_type = data.get("user_type")
        logging.info(f"The user type is {user_type}")
        query = "select * from `user_authentication` where username=%s or email=%s;"
        params=[username, email]
        result = execute_(database, query, params)
        status = 1
        logging.info(f"The result is {result}")
        if result:
            message="Already there are users registered with the entered username or email"
            return {
                "flag" : False,
                "message" : message 
            }
        else:
            query = 'INSERT INTO `user_authentication` (`email`, `username`, `password`, `confirm_password`, `user_type`,`status`) VALUES (%s, %s, %s, %s, %s, %s);'
            params = [email, username, password, confirm_password, user_type, status]
            result = insert_query(database, query, params)
            logging.info(f"The result is {result}")
            if result:
                return {
                    "flag" : True,
                    "message" : "User registered successfully!"
                }
            else:
                return {
                    "flag" : False,
                    "message" : "Something went wrong with registration."
                }
                
@app.route("/login_user", methods=["GET","POST"])
def login_user():
    email = os.getenv("email")
    logging.info(f"The Email is {email}")
    password = os.getenv("password")
    logging.info(f"The Password is {password}")
    database = "user_management"
    logging.info(f"The Request Method is {request.method}")
    if request.method == "POST":
        data = request.get_json()
        logging.info(f"Request Data is {data}")
        username_or_email = data.get("username_or_email","")
        logging.info(f"The user name (or) email is {username_or_email}")
        password = data.get("password","")
        logging.info(f"The password is {password}")
        query = """
        select * from `user_authentication`
        where (username=%s or email=%s) and password=%s;
        """
        params=[username_or_email, username_or_email, password]
        result = execute_(database, query, params)
        logging.info(f"The result is {result}")
        if not result:
            message = "Username (or) Email not found!"
            return {
                "flag" : False,
                "message" : message
            }
        user_info = result[0]
        to_email = result[0]["email"]
        otp = generate_otp()
        otp_expiry = (datetime.now() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
        otp_update_query = """
        update `user_authentication`
        set otp = %s, otp_expiry = %s
        where email = %s or username = %s;
        """
        params = [otp, otp_expiry, username_or_email, username_or_email]
        result = update_query(database, otp_update_query, params)
        logging.info(f"The Result is {result}")
        info = fetch_email_body()
        logging.info(f"The email_template is {info}")
        query = """
        SELECT `username`,`status` FROM `user_authentication`
        WHERE username = %s or email = %s;
        """
        params = [username_or_email, username_or_email]
        name_result = execute_(database, query, params)
        name = name_result[0]["username"]
        status = name_result[0]["status"]
        if status == "0":
            message = "Account Locked!"
            return {
                "flag" : "locked",
                "message" : message
            }
        if info:
            try:
                logging.info(f"The type of info is {type(info)}")
                logging.info(f"The type of info[0] is {type(info[0])}")
                logging.info(f"The type of info[0][info] is {type(info[0]['info'])}")
                logging.info(f"The info[0]['info'] is {info[0]['info']}")
                raw_info = info[0]["info"]
                logging.info(f"Raw info before parsing: {raw_info}")
                parsed_info = json.loads(raw_info)

                # try:
                #     parsed_info = json.loads(clean_str)
                # except json.JSONDecodeError as e:
                #     logging.exception(f"The json error occured with exception: {e}")
                #     logging.exception(f"Broken_str:{clean_str}")
                
                # info[0]['info'] = json.loads(info[0]["info"].replace('\n', '\\n').replace('\r', '\\r'))
                # info_dict = info[0]
                # if isinstance(info_dict, dict) and "info" in info_dict and isinstance(info_dict["info"], dict):
                from_email = parsed_info["email"]
                logging.info(f"The from email is {from_email}")
                email_subject =  parsed_info["subject"]
                logging.info(f"The subject is {email_subject}")
                email_body = parsed_info["body"]
                logging.info(f"The email body is {email_body}")
                subject_template = Template(email_subject)
                logging.info(f"The subject template is {subject_template}")
                body_template = Template(email_body)
                logging.info(f"The body template is {body_template}")
                subject = subject_template.render(username=name, otp=otp)
                body = body_template.render(username=name, otp=otp)
                
                send_email(to_email, subject, body)
                logging.info(f"The Email sent to {to_email}")
            except Exception as e:
                logging.exception(f"Error occured with Exception {e}")
                message = "Internal error while sending OTP"
                return {
                    "flag" : False,
                    "message" : message
                }
        
        return {
            "flag" : True,
            "message" : "Otp Generated Successfully!"
        }
from flask import request
from datetime import datetime
import logging

@app.route("/validate_otp", methods=["POST"])
def validate_otp():
    database = "user_management"
    data = request.get_json()
    logging.info(f"The Data obtained is {data}")
    otp_input = data.get("otp")
    logging.info(f"The OTP Entered is {otp_input}")
    username_or_email = data.get("username_or_email")
    logging.info(f"The Username (or) Email entered is {username_or_email}")
    if not otp_input or not username_or_email:
        return {"flag": "error", "message": "Missing OTP or email/username."}

    try:
        otp_query = """
        SELECT `otp`, `otp_expiry`, `otp_attempts`, `status`
        FROM `user_authentication`
        WHERE username = %s OR email = %s;
        """
        params = [username_or_email, username_or_email]
        result = execute_(database, otp_query, params)
        if not result:
            return {"flag": "error", "message": "User not found."}
        otp = result[0]["otp"]
        logging.info(f"The OTP From database is {otp}")
        otp_expiry = result[0]["otp_expiry"]
        logging.info(f"The OTP Expiry from database is {otp_expiry}")
        attempts = result[0]["otp_attempts"]
        logging.info(f"The No of Attempts available are {attempts}")
        status = result[0]["status"]
        logging.info(f"The Status is {status}")
        now = datetime.now()
        otp_expiry = datetime.strptime(otp_expiry, '%Y-%m-%d %H:%M:%S')
        if status == 0:
            return {"flag": "locked", "message": "Account is locked. Contact support."}
        if now > otp_expiry:
            return {"flag": "expired", "message": "OTP has expired. Please request a new one."}
        if otp_input == str(otp):
            reset_attempts_query = """
            UPDATE `user_authentication`
            SET `otp_attempts` = 0
            WHERE username = %s OR email = %s;
            """
            update_query(database, reset_attempts_query, params)
            return {"flag": "success", "message": "OTP Verified Successfully!"}
        attempts += 1
        if attempts >= 3:
            # Lock account
            lock_query = """
            UPDATE `user_authentication`
            SET `status` = 0, `otp_attempts` = 3
            WHERE username = %s OR email = %s;
            """
            update_query(database, lock_query, params)
            return {"flag": "locked", "message": "Account locked after 3 failed OTP attempts."}
        else:
            increment_attempt_query = """
            UPDATE `user_authentication`
            SET `otp_attempts` = %s
            WHERE username = %s OR email = %s;
            """
            update_query(database, increment_attempt_query, [attempts] + params)
            return {"flag": "invalid", "message": f"Invalid OTP. {3 - attempts} attempt(s) left."}
    except Exception as e:
        logging.exception("Exception during OTP validation")
        return {"flag": "error", "message": "Something went wrong. Try again."}

        
        
        
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8081)