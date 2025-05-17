FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install -r backend/bounding_box_detection_api/requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8088

CMD ["python", "backend/bounding_box_detection_api/bounding_box_detection_api.py"]