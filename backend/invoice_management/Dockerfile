FROM python:3.10-slim

RUN apt-get update && apt-get install -y poppler-utils && apt-get clean

WORKDIR /app

COPY . .

RUN pip install -r backend/invoice_management/requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8084

CMD ["python", "backend/invoice_management/invoice_management.py"]