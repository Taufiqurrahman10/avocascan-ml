# Use official lightweight Python image
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    PORT=7860

# Set working directory
WORKDIR /app

# Install system dependencies required for image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose ports (Hugging Face Spaces default is 7860, standard API is 8000)
EXPOSE 7860 8000

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Pre-download u2netp.onnx into appuser home folder during Docker build
RUN mkdir -p /home/appuser/.u2net && \
    apt-get update && apt-get install -y --no-install-recommends curl && \
    curl -L -o /home/appuser/.u2net/u2netp.onnx https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx && \
    chown -R appuser:appuser /home/appuser/.u2net && \
    rm -rf /var/lib/apt/lists/*

USER appuser

# Run FastAPI application using uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
