FROM python:3.9-slim

WORKDIR /app

# Install dependencies for Tesseract and other required libraries
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libsm6 libxext6 libxrender-dev \
    libicu-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the application code into the container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r backend/extraction_api/requirements.txt

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Expose port (assuming your Flask API runs on 8085)
EXPOSE 8085

# Command to run the extraction API
CMD ["python", "backend/extraction_api/extraction_api.py"]