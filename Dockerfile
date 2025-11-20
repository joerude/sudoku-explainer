# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Install system dependencies for OpenCV, Tesseract, and libGL
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port (adjust if your web/app.py uses a different port)
EXPOSE 8000

# Set PYTHONPATH so sudoku_explainer is importable
ENV PYTHONPATH=/app

# Default command (adjust if your entrypoint is different)
CMD ["python", "web/app.py"]
