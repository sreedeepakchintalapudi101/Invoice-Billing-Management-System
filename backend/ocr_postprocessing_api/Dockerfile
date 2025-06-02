FROM paddlepaddle/paddle:2.4.2

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    tesseract-ocr \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY backend/ocr_postprocessing_api/requirements.txt ./requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8087

CMD ["python", "backend/ocr_postprocessing_api/ocr_postprocessing_api.py"]