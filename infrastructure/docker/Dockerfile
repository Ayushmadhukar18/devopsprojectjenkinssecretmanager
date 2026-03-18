FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer cache optimization)
COPY src/main/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/main/app/ .

# Non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
