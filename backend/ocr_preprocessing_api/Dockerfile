FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install -r backend/ocr_preprocessing_api/requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8087

CMD ["python", "backend/ocr_preprocessing_api/ocr_preprocessing_api.py"]