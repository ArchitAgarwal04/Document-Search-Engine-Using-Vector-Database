FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# - curl        : required by docker-compose healthcheck (CMD curl -f ...)
# - libgomp1    : required at runtime by faiss-cpu and PyTorch (sentence-transformers)
# - libssl-dev  : required by the 'cryptography' package (python-jose)
# - libffi-dev  : required by the 'cffi' wheel used by cryptography
# - git         : required by sentence-transformers for model downloads
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libgomp1 \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copy app source
COPY . .

# Create data directories
RUN mkdir -p data/uploads data/chroma_db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
