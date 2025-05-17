FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    tesseract-ocr \
    build-essential \
    cmake \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=100 --retries=10 -r backend/bounding_box_detection_api/requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8088

CMD ["python", "backend/bounding_box_detection_api/bounding_box_detection_api.py"]
