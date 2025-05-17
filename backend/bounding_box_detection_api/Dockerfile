FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install -r backend/bounding_box_detection_api/requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8088

CMD ["python", "backend/bounding_box_detection_api/bounding_box_detection_api.py"]