FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install -r backend/ocr_preprocessing/requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8087

CMD ["python", "backend/ocr_preprocessing_api/ocr_preprocessing_api.py"]