FROM python:3.12-slim

# System deps needed by chromadb (native extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better layer caching)
COPY pyproject.toml .
RUN pip install --no-cache-dir \
    fastapi==0.115.5 \
    "uvicorn[standard]==0.32.1" \
    pydantic-settings==2.6.1 \
    "openai>=1.55" \
    "chromadb>=0.5" \
    python-multipart==0.0.12

# Copy source + baked data
COPY . .

# Ensure data dirs exist
RUN mkdir -p data/chroma

EXPOSE 8000

# PORT is set by Render; fallback to 8000 locally
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
