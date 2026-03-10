FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Download spaCy model (workers also need it for claim type routing)
RUN python -m spacy download en_core_web_lg

COPY . .

CMD ["celery", "-A", "app.workers.celery_app", "worker", "--loglevel=info", "--concurrency=10", "-Q", "verification"]
