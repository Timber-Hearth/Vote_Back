# syntax=docker/dockerfile:1

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY req.txt ./req.txt
RUN python -c "from pathlib import Path; Path('/tmp/requirements.txt').write_text(Path('req.txt').read_text(encoding='utf-16'), encoding='utf-8')" \
    && python -m pip install --upgrade pip \
    && python -m pip install -r /tmp/requirements.txt

COPY . .

EXPOSE 8080

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
