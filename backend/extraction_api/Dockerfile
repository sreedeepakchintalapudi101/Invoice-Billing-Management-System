FROM python:3.9-slim

WORKDIR /app

# Install only what's necessary: Tesseract and Poppler
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies with retries and timeout handling
RUN pip install --upgrade pip && pip install --no-cache-dir -r backend/extraction_api/requirements.txt

ENV PYTHONPATH=/app

# Expose the service port
EXPOSE 8085

# Default command to run the app
CMD ["python", "backend/extraction_api/extraction_api.py"]
