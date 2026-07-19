FROM python:3.12-slim

# Python behavior stays predictable inside containers.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies are installed first so Docker layer caching works better.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App source is copied after dependencies to avoid reinstalls on code-only changes.
COPY . .

# Uvicorn runs on all interfaces so container port mapping works.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
