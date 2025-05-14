FROM python:3.10-slim

WORKDIR /app

# Install required system packages including libGL
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libglib2.0-0 \
    libgl1-mesa-glx \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r backend/extraction_api/requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8085

CMD ["python", "backend/image_conversion_api/image_conversion_api.py"]
