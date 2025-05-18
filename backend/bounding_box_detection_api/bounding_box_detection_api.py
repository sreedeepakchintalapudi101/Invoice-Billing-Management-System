from flask import Flask, request
from flask_cors import CORS
import logging
import os
import cv2
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

from flask import request
import os
import logging
import cv2
from ultralytics import YOLOv10

@app.route("/bounding_box_detection_api", methods=["GET", "POST"])
def bounding_box_detection_api():
    database = "extraction_management"
    data = request.get_json()
    try:
        logging.info(f"Request Data is {data}")
        
        invoice_id = data.get("invoice_id", "")
        grey_image_paths = data.get("grey_image_paths", [])
        
        logging.info(f"Invoice ID: {invoice_id}")
        logging.info(f"Grey Image Paths: {grey_image_paths}")

        model = YOLOv10.from_pretrained("juliozhao/DocLayout-YOLO-DocStructBench")
        if not model:
            logging.error("Model not loaded!")
            return {"flag": False, "message": "Model not loaded!"}

        if not invoice_id or not grey_image_paths:
            logging.warning("Missing invoice_id or grey_image_paths")
            return {"flag": False, "message": "Missing required fields"}

        all_crop_paths = []

        for grey_image_path in grey_image_paths:
            if not os.path.exists(grey_image_path):
                logging.warning(f"File does not exist: {grey_image_path}")
                continue

            logging.info(f"Processing: {grey_image_path}")
            det_res = model.predict(grey_image_path, imgsz=1024, conf=0.2, device="cuda:0")
            img = cv2.imread(grey_image_path)
            if img is None:
                logging.error(f"Failed to read image: {grey_image_path}")
                continue
            base_path = os.path.dirname(grey_image_path)
            image_file_name = os.path.splitext(os.path.basename(grey_image_path))[0]  # e.g., "image_01"
            output_dir = os.path.join(base_path, image_file_name)
            os.makedirs(output_dir, exist_ok=True)
            logging.info(f"Cropped images will be saved in: {output_dir}")

            crop_paths = []

            for idx, box in enumerate(det_res[0].boxes):
                x_min, y_min, x_max, y_max = map(int, box.xyxy[0].tolist())
                cropped_image = img[y_min:y_max, x_min:x_max]
                crop_path = os.path.join(output_dir, f"cropped_region_{idx+1}.jpg")
                cv2.imwrite(crop_path, cropped_image)
                crop_paths.append(crop_path)
                logging.info(f"Saved cropped image: {crop_path}")
            
            all_crop_paths.extend(crop_paths)

        return {
            "flag": True,
            "message": "Cropped images saved successfully",
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