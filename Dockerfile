FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create data directory
RUN mkdir -p ./data

# Create non-root user
RUN useradd -m -u 1000 cssuser && chown -R cssuser:cssuser /app
USER cssuser

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "src.main"] 