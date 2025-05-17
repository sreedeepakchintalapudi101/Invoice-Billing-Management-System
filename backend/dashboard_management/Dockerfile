FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install -r backend/dashboard_management/requirements.txt

ENV PYTHONPATH=/app

RUN pip install flask_cors

EXPOSE 8082

CMD ["python", "backend/dashboard_management/dashboard_management.py"]