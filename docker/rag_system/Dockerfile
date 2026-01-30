FROM ghcr.io/astral-sh/uv:0.6.14-python3.10-bookworm

WORKDIR /app

# Install additional system dependencies for lxml and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libavif-dev pkg-config \
    libjpeg-dev \
    gcc unzip zip \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY Src/requirements.txt .
RUN uv pip install -r requirements.txt --system

COPY Src/ .

# Create directory structure for Alembic (matching the correct path)
RUN mkdir -p /app/models/db_Schema/minirag/

# Copy alembic.ini to the correct location
COPY docker/rag_system/alembic.ini /app/models/db_Schema/minirag/alembic.ini

COPY docker/rag_system/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]