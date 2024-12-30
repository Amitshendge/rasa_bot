# Start with a lightweight Ubuntu base image
FROM ubuntu:22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-venv \
    python3-pip \
    curl \
    nano \
    git \
    build-essential \
    libffi-dev \
    libssl-dev \
    libsqlite3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /app

# Copy your Rasa project files into the container
COPY requirements.txt /app/
# Upgrade pip and install dependencies
RUN python3.10 -m pip install --upgrade pip setuptools wheel

# Install Rasa dependencies
RUN pip install --root-user-action=ignore --no-cache-dir -r requirements.txt

COPY app /app
RUN rasa train

CMD ["bash", "-c", "rasa run & rasa run actions & streamlit run streamlit_app/test.py --server.port=8080 --server.address=0.0.0.0"]

