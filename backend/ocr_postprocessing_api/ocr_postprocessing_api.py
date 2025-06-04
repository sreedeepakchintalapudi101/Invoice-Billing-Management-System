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
import cv2
from doclayout_yolo import YOLOv10
from huggingface_hub import hf_hub_download
import torch
import numpy as np
import pandas as pd
import tensorflow as tf
from paddleocr import PaddleOCR, draw_ocr
import tensorflow as tf
import pymysql

app = Flask(__name__)
CORS(app)

import logging
import dotenv
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
load_dotenv()

os.environ["CUDA_VISIBLE_DEVICES"] = os.getenv("CUDA_VISIBLE_DEVICES", "-1")

logging.info("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     headers = [
#         logging.StreamHandler()
#     ]
# )

@app.route("/", methods=["GET", "POST"])
def home():
    message = "Successfully Launched!"
    return {
        "flag" : True,
        "message" : message
    }
    
@app.route("/ocr_postprocessing_api", methods=["GET","POST"])
def ocr_postprocessing_api():
    logging.info(f"Entering into the ocr_postprocessing_api route")
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
        if not select_result:
            message = "No OCR data found"
            logging.error("No result found for invoice_id: %s", invoice_id)
            return {
                "flag": False, 
                "message": message
            }
        try:
            ocr_dict = json.loads(select_result[0].get("extracted_text", "{}"))
        except Exception as e:
            logging.error("Failed to load JSON from extracted_text: %s", e)
            message = "Invalid extracted_text format"
            return {
                "flag": False, 
                "message": message
            }
        logging.info(f"The ocr dict is {ocr_dict}")
        processed_dict = {}
        logging.info(f"The processed dict is {processed_dict}")
        template_type = ""
        for item in ocr_dict["extracted"][0]["ocr_data"]:
            if item["label"] == "plain text":
                if "Amazon.in" in item["text"] or "amazon" in item["text"].lower() or "amazon" in item["text"]:
                    template_type = "Amazon"
                elif 1600 < item["bbox"][0] < 1900 and 550 < item["bbox"][1] < 570 and 3050 < item["bbox"][2] < 3100 and 1000 < item["bbox"][3] < 1100:
                    raw_text = item["text"]
                    logging.info(f"The raw text is {raw_text}")
                    lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip() ]
                    logging.info(f"The lines at billing address are {lines}")
                    billing_address_lines = []
                    for line in lines:
                        if "Billing Address" in line:
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
                    logging.info(f"the lines are {lines}")
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
                elif 200 < item["bbox"][0] < 300 and 1000 < item["bbox"][1] < 1200 and 1300 < item["bbox"][2] < 1500 and 1200 < item["bbox"][3] < 1400:
                    raw_text = item["text"]
                    logging.info(f"The raw text is {raw_text}")
                    lines = [line.strip() for line in item["text"].split("\n") if line.strip()]
                    logging.info(f"The lines are {lines}")
                    for line in lines:
                        logging.info(f"The line is {line}")
                        if "PAN No" in line:
                            logging.info(f"The current line is {line}")
                            match = re.search(r"^PAN No:\s*(.+)$", line)
                            logging.info(f"The Match is {match}")
                            logging.info(f"The Group 0 is {match.group(0)}")
                            logging.info(f"The Group 1 is {match.group(1)}")
                            if match:
                                processed_dict["PAN No"] = match.group(1)
                                logging.info(f"The processed dict of PAN No is {processed_dict['PAN No']}")
                        if "GST Registration No" in line:
                            logging.info(f"The current line is {line}")
                            match = re.search(r"^GST Registration No:\s*(.+)$", line)
                            logging.info(f"The Match is {match}")
                            logging.info(f"The Group 0 is {match.group(0)}")
                            logging.info(f"The Group 1 is {match.group(1)}")
                            if match:
                                processed_dict["GST Registration No"] = match.group(1)
                                logging.info(f"The processed dict of GST Registration No is {processed_dict['GST Registration No']}")
                elif 200 < item["bbox"][0] < 300 and 1900 < item["bbox"][1] < 2300 and 1200 < item["bbox"][2] < 1400 and 2050 < item["bbox"][3] < 2450:
                    raw_text = item["text"]
                    logging.info(f"The raw text is {raw_text}")
                    lines = [item.strip() for item in raw_text.split("\n") if item.strip()]
                    logging.info(f"The lines are {lines}")
                    for line in lines:
                        if "Order Number" in line:
                            logging.info(f"The current line is {line}")
                            match = re.search(r"^Order Number:\s*(.+)$", line)
                            logging.info(f"The Match is {match}")
                            logging.info(f"The Group 0 is {match.group(0)}")
                            logging.info(f"The Group 1 is {match.group(1)}")
                            if match:
                                processed_dict["Order Number"] = match.group(1)
                                logging.info(f"The processed dict of Order Number is {processed_dict['Order Number']}")
                        if "Order Date" in line:
                            logging.info(f"The current line is {line}")
                            match = re.search(r"^Order Date:\s*(.+)$", line)
                            logging.info(f"The Match is {match}")
                            logging.info(f"The Group 0 is {match.group(0)}")
                            logging.info(f"The Group 1 is {match.group(1)}")
                            if match:
                                processed_dict["Order Date"] = match.group(1)
                                logging.info(f"The processed dict of Order Data is {processed_dict['Order Date']}")
            elif item["label"] == "table":
                logging.info(f"The detection type is {item['label']}")
                logging.info(f"The bounding boxes are {item['bbox']}")
                path_query = """
                SELECT `image_path` FROM `raw_ocr`
                WHERE `invoice_id` = %s;
                """
                params = [invoice_id]
                result = execute_("extraction_management", path_query, params)
                image_path = result[0]["image_path"]
                logging.info(f"The image path is {image_path}")
                parts = image_path.rsplit("/", 1)
                logging.info(f"The parts are {parts}")
                filename = parts[1]
                logging.info(f"The file name is {filename}")
                new_image_path = f"{parts[0]}/{filename}"
                logging.info(f"The new image path is {new_image_path}")
                image = cv2.imread(new_image_path)
                coords = item["bbox"]
                logging.info(f"The coordinates are {coords}")
                x_1, y_1, x_2, y_2 = coords[0], coords[1], coords[2], coords[3]
                logging.info(f"The x_1 coordinate is {x_1}")
                logging.info(f"The y_1 coordinate is {y_1}")
                logging.info(f"The x_2 coordinate is {x_2}")
                logging.info(f"The y_2 coordinate is {y_2}")
                cropped_image = image[y_1:y_2, x_1:x_2]
                parts = image_path.rsplit("/", 2)
                logging.info(f"The parts are {parts}")
                filename = parts[2].replace(parts[2], "table_detected_image.jpg")
                logging.info(f"The file name is {filename}")
                new_image_path = f"{parts[0]}/{parts[1]}/{filename}"
                logging.info(f"The new image path is {new_image_path}")
                cv2.imwrite(new_image_path, cropped_image)
                ocr = PaddleOCR(lang='en')
                # image_path = "C:/Users/91798/Desktop/Invoice Billing Management System/INV3cf69342ff1a46b7/table_crop_0.jpg"
                image_cv = cv2.imread(new_image_path)
                image_height = image_cv.shape[0]
                image_width = image_cv.shape[1]
                output = ocr.ocr(new_image_path)[0]
                logging.info(f"The image height is {image_height}")
                logging.info(f"The image width is {image_width}")
                logging.info(f"The output is {output}")
                boxes = [line[0] for line in output]
                texts = [line[1][0] for line in output]
                probabilities = [line[1][1] for line in output]
                logging.info(f"The boxes are {boxes}")
                logging.info(f"The texts are {texts}")
                logging.info(f"The probabilities are {probabilities}")
                image_boxes = image_cv.copy()
                for box, text in zip(boxes, texts):
                    cv2.rectangle(image_boxes, (int(box[0][0]), int(box[0][1])), (int(box[2][0]), int(box[2][1])), (0,255,0), 1)
                parts = image_path.split("/", 1)
                logging.info(f"The parts are {parts}")
                filename = "detection.jpg"
                logging.info(f"The file name is {filename}")
                new_image_path = f"{parts[0]}/{filename}"
                logging.info(f"The new image path {new_image_path}")
                cv2.imwrite(new_image_path, image_boxes)
                im = image_cv.copy()
                horiz_boxes = []
                vert_boxes = []

                for box in boxes:
                    x_h, x_v = 0,int(box[0][0])
                    y_h, y_v = int(box[0][1]),0
                    width_h,width_v = image_width, int(box[2][0]-box[0][0])
                    height_h,height_v = int(box[2][1]-box[0][1]),image_height
                    
                    horiz_boxes.append([x_h,y_h,x_h+width_h,y_h+height_h])
                    vert_boxes.append([x_v,y_v,x_v+width_v,y_v+height_v])
                    
                    cv2.rectangle(im,(x_h,y_h), (x_h+width_h,y_h+height_h),(0,0,255),1)
                    cv2.rectangle(im,(x_v,y_v), (x_v+width_v,y_v+height_v),(0,255,0),1)
                parts = image_path.split("/", 1)
                logging.info(f"The parts are {parts}")
                filename = "horiz_vert.jpg"
                logging.info(f"The filename is {filename}")
                new_image_path = f"{parts[0]}/{filename}"
                logging.info(f"The new image path is {new_image_path}")
                cv2.imwrite(new_image_path, im)
                horiz_out = tf.image.non_max_suppression(
                    horiz_boxes,
                    probabilities,
                    max_output_size = 1000,
                    iou_threshold=0.1,
                    score_threshold=float('-inf'),
                    name=None
                )
                logging.info(f"The horizontal output is {horiz_out}")
                horiz_lines = np.sort(np.array(horiz_out))
                logging.info(f"The horizontal lines are {horiz_lines}")
                im_nms = image_cv.copy()
                for val in horiz_lines:
                    cv2.rectangle(im_nms, (int(horiz_boxes[val][0]),int(horiz_boxes[val][1])), (int(horiz_boxes[val][2]),int(horiz_boxes[val][3])),(0,0,255),1)
                parts = image_path.rsplit("/", 1)
                logging.info(f"the parts are {parts}")
                filename = "im_nms.jpg"
                logging.info(f"The filename is {filename}")
                new_image_path = f"{parts[0]}/{filename}"
                logging.info(f"The new image path is {new_image_path}")
                cv2.imwrite(new_image_path, im_nms)
                vert_out = tf.image.non_max_suppression(
                    vert_boxes,
                    probabilities,
                    max_output_size = 1000,
                    iou_threshold=0.1,
                    score_threshold=float('-inf'),
                    name=None
                )
                vert_lines = np.sort(np.array(vert_out))
                logging.info(f"The vertical lines are {vert_lines}")
                for val in vert_lines:
                    cv2.rectangle(im_nms, (int(vert_boxes[val][0]),int(vert_boxes[val][1])), (int(vert_boxes[val][2]),int(vert_boxes[val][3])),(255,0,0),1)
                cv2.imwrite(new_image_path, im_nms)
                out_array = [["" for i in range(len(vert_lines))] for j in range(len(horiz_lines))]
                logging.info(f"The shape of np.array is {np.array(out_array).shape}")
                logging.info(f"The output is {out_array}")
                unordered_boxes = []
                for i in vert_lines:
                    logging.info(f"The vertical boxes are {vert_boxes[i]}")
                    unordered_boxes.append(vert_boxes[i][0])
                ordered_boxes = np.argsort(unordered_boxes)
                logging.info(f"The ordered boxes are {ordered_boxes}")
                for i in range(len(horiz_lines)):
                    for j in range(len(vert_lines)):
                        resultant = intersection(horiz_boxes[horiz_lines[i]], vert_boxes[vert_lines[ordered_boxes[j]]] )
                        for b in range(len(boxes)):
                            the_box = [boxes[b][0][0],boxes[b][0][1],boxes[b][2][0],boxes[b][2][1]]
                            if(iou(resultant,the_box)>0.1):
                                out_array[i][j] = texts[b]
                out_array=np.array(out_array)
                logging.info(f"The out array is {out_array}")
                
                html_table = convert_to_html_table(out_array.tolist())
                processed_dict['html_table'] = html_table
                
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
                    "extracted_dict" : processed_dict,
                    "html_table" : html_table
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
                    "extracted_dict" : processed_dict,
                    "html_table" : html_table
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
        message = f"Something went wrong with exception {e}!"
        logging.info(f"Error occured with Exception {e}")
        return {
            "flag" : False,
            "message" : message
        }

def intersection(box_1, box_2):
    return [box_2[0], box_1[1],box_2[2], box_1[3]]

def iou(box_1, box_2):
    x_1 = max(box_1[0], box_2[0])
    y_1 = max(box_1[1], box_2[1])
    x_2 = min(box_1[2], box_2[2])
    y_2 = min(box_1[3], box_2[3])
    inter = abs(max((x_2 - x_1, 0)) * max((y_2 - y_1), 0))
    if inter == 0:
        return 0
    box_1_area = abs((box_1[2] - box_1[0]) * (box_1[3] - box_1[1]))
    box_2_area = abs((box_2[2] - box_2[0]) * (box_2[3] - box_2[1]))
    return inter / float(box_1_area + box_2_area - inter)

def convert_to_html_table(table_data):
    html = "<table border='1' style='border-collapse: collapse;'>"
    for row in table_data:
        html += "<tr>"
        for cell in row:
            html += f"<td style='padding: 5px;'>{cell}</td>"
        html += "</tr>"
    html += "</table>"
    return html

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8087)