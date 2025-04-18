FROM python:3.12.7-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies for MySQL client
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy only the app folder from your local structure
COPY app/ /app/

# ✅ Run aggregator.py from inside /app
CMD ["python", "aggregator.py"]