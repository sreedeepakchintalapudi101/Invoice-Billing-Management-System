FROM python:3.10-slim

WORKDIR /app

COPY . .

ENV PYTHONPATH=/app

RUN pip install -r backend/table_detection_api/requirements.txt

EXPOSE 8086

CMD ["python", "backend/table_detection_api/table_detection_api.py"]