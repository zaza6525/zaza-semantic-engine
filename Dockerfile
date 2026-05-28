# Zaza Semantic Engine — Docker
# Usage:
#   docker build -t zaza-semantic-engine .
#   docker run --rm -it -p 8000:8000 -v $(pwd)/data:/app/data zaza-semantic-engine

FROM python:3.12-slim

WORKDIR /app

# System deps for building C extensions (sentence-transformers, lxml)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy and install
COPY . .
RUN pip install --no-cache-dir -e ".[all]"

# Create data directory for ChromaDB persistence
RUN mkdir -p /app/data

# Default: run CLI (override with CMD)
ENTRYPOINT ["zaza"]
CMD ["--help"]

# To run the API server:
#   docker run --rm -it -p 8000:8000 zaza-semantic-engine api --port 8000
