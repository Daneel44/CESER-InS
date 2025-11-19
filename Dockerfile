
# 1) Base image
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Optional: set the port once, used by EXPOSE and Gunicorn
    PORT=8000

# 2) System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# 3) Create non-root user & workdir
RUN useradd -m appuser
WORKDIR /app

# 4) Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copy application code
COPY . .

# 6) Permissions and user
RUN chown -R appuser:appuser /app
USER appuser

# 7) Expose port & run Gunicorn
EXPOSE 8000

# If your Flask app is in app.py and the Flask instance is named "app":
#   module = app
#   flask object = app
# so WSGI path is "app:app"
#
# Tune workers/threads as needed; a common rule: workers = 2*CPU+1
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "app:app"]
