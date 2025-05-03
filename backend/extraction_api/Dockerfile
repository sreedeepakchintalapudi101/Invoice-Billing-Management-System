FROM python:3.9-slim

WORKDIR /app

# Install dependencies for Tesseract, Poppler (PDF to image), and OpenCV
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libsm6 libxext6 libxrender-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libicu-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the entire project into the container
COPY . .

# Install Python dependencies with retries and increased timeout
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=100 --retries=10 \
    --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    -r backend/extraction_api/requirements.txt

# Set Python path for app imports
ENV PYTHONPATH=/app

# Expose the API port
EXPOSE 8085

# Command to run the app
CMD ["python", "backend/extraction_api/extraction_api.py"]