FROM python:3.10-slim

WORKDIR /app

COPY . .

ENV PYTHONPATH=/app

RUN pip install -r backend/email_management/requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8083

CMD ["python", "backend/email_management/email_management.py"]