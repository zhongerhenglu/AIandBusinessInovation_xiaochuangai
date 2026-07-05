FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/archive data/cross_sections knowledge/wiki_storage knowledge/graph_storage knowledge/chroma knowledge/change_logs logs output

ENV PYTHONPATH=/app

CMD ["python", "start_background_service.py"]