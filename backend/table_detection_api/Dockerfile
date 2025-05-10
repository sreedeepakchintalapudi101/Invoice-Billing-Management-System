FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install -r backend/table_detection_api/requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8086

CMD["python", "backend/table_detection_api/table_detection_api.py"]