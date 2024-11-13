# Use Python 3.12.5 as base image
FROM python:3.12.5-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for MySQL and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    pkg-config \
    libpoppler-cpp-dev \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy and install core requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p storage/pdf_uploads storage/txt_outputs storage/table_outputs storage/logs

# Expose the port the app runs on
EXPOSE 5106

# Command to run the application
CMD ["python", "main.py"]
