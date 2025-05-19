from flask import Flask, request
from flask_cors import CORS
import logging
import os
import cv2
from doclayout_yolo import YOLOv10
from huggingface_hub import hf_hub_download
import 
import pytesseract
from datetime import datetime
import torch
from backend.database.db_utils import get_connection, execute_, insert_query, update_query
app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level = logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers = [
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

@app.route("/bounding_box_detection_api", methods=["GET", "POST"])
def bounding_box_detection_api():
    database = "extraction_management"
    try:
        data = request.get_json()
        logging.info(f"Request Data is {data}")
        
        invoice_id = data.get("invoice_id", "")
        grey_image_paths = data.get("grey_image_paths", [])
        update_flag = data.get("update_flag", "")
        
        logging.info(f"Invoice ID: {invoice_id}")
        logging.info(f"Grey Image Paths: {grey_image_paths}")
        logging.info(f"Update Flag is {update_flag}")
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not invoice_id or not grey_image_paths:
            logging.warning("Missing invoice_id or grey_image_paths")
            return {"flag": False, "message": "Missing required fields"}
        file_path = hf_hub_download(
            repo_id = "juliozhao/DocLayout-YOLO-DocStructBench",
            filename = "doclayout_yolo_docstructbench_imgsz1024.pt"
        )
        model = YOLOv10(file_path)
        if not model:
            logging.error("Model not loaded!")
            return {"flag": False, "message": "Model not loaded!"}

        extraction_dict = {
            "invoice_id" : invoice_id,
            "extracted" : []
        }
        all_crop_paths = []
        for grey_image_path in grey_image_paths:
            temp_dict = {
                "image_path" : grey_image_path,
                "ocr_data" : []
            }
            crop_paths = []
            if not os.path.exists(grey_image_path):
                logging.warning(f"File does not exist: {grey_image_path}")
                continue
            logging.info(f"Processing: {grey_image_path}")
            img = cv2.imread(grey_image_path)
            if img is None:
                logging.error(f"Failed to read image: {grey_image_path}")
                continue
            det_res = model.predict(
                grey_image_path, 
                imgsz = 1024, 
                conf = 0.2, 
                device = "cuda:0" if torch.cuda.is_available() else "cpu"
                )
            image_file_name = os.path.splitext(os.path.basename(grey_image_path))[0]
            logging.info(f"The Image File Name is {image_file_name}")
            output_dir = os.path.join(os.path.dirname(grey_image_path), "crops_" + invoice_id)
            os.makedirs(output_dir, exist_ok=True)
            logging.info(f"Cropped images will be saved in: {output_dir}")
            for index, box in enumerate(det_res[0].boxes):
                x_min, y_min, x_max, y_max = map(int, box.xyxy[0].tolist())
                cropped_image = img[y_min:y_max, x_min:x_max]
                label_id = int(box.cls[0])
                label_name = det_res[0].names[label_id]
                text = pytesseract.image_to_string(cropped_image).strip()
                
                crop_path = os.path.join(output_dir, f"{image_file_name}_crop_{index + 1}.jpg")
                cv2.imwrite(crop_path, cropped_image)

                temp_dict["ocr_data"].append({
                    "id": index + 1,
                    "label": label_name,
                    "bbox": [x_min, y_min, x_max, y_max],
                    "text": text
                })
                
                crop_paths.append(crop_path)
                all_crop_paths.append(crop_path)
                logging.info(f"Saved cropped image: {crop_path}")
                
        extraction_dict["extracted"].append(temp_dict)
        
        logging.info(f"THe Extracted Dict is {extraction_dict}")
        
        if update_flag == "new":
            insertion_query = """
            INSERT INTO `raw_ocr` (invoice_id, image_path, extracted_text, created_at, updated_at)
            VALUES
            (%s, %s, %s, %s, %s);
            """
            params = [invoice_id, grey_image_paths, str(extraction_dict), current_time, current_time]
            result = insert_query(database, insertion_query, params)
            logging.info(f"The result is {result}")
            message = "The Extraction is Done Successfully!"
            return {
                "flag" : True,
                "message" : message,
                "file_paths" : all_crop_paths
            }
        if update_flag == "update":
            updation_query = """
            UPDATE `raw_ocr` SET `extracted_data` = %s, updated_at = %s
            WHERE `invoice_id` = %s and grey_image_path = %s;
            """
            params = [str(extraction_dict), current_time, invoice_id, grey_image_paths]
            result = update_query(database, updation_query, params)
            logging.info(f"The result is {result}")
            message = "OCR Data Updated Successfully!"
            return {
                "flag": True,
                "message": message,
                "file_paths": all_crop_paths
            }

    except Exception as e:
        logging.exception("Error occurred during bounding box detection")
        return {
            "flag": False,
            "message": f"Something went wrong: {str(e)}"
        }

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8088)