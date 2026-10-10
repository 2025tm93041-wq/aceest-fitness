# ---- Stage 1: install dependencies into a wheel cache ----
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: minimal runtime image ----
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_PATH=/data/aceest_fitness.db
WORKDIR /app

COPY --from=builder /install /usr/local
COPY app.py .

# Run as a non-root user
RUN useradd --create-home appuser && mkdir /data && chown appuser /data
USER appuser

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
