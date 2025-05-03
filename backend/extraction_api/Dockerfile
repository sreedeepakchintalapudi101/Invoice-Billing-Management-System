FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y poppler-utils && apt-get clean

RUN apt-get update && apt-get install -y tesseract-ocr && apt-get install -y libsm6 libxext6 libxrender-dev && apt-get cleam

COPY . .

RUN pip install -r backend/extraction_api/requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8085

CMD ["python", "backend/extraction_api/extraction_api.py"]