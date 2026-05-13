# ─────────────────────────────────────────────
# OCP AI Monitoring Agent — Dockerfile
# ─────────────────────────────────────────────
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install PyTorch CPU version first
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir

# Install all other dependencies
RUN pip install -r requirements.txt --no-cache-dir

# Copy entire project
COPY . .

# Expose dashboard port
EXPOSE 5000

# Run the scheduler
CMD ["python", "scheduler.py"]