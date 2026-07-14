FROM python:3.12-slim

# I keep Python behavior predictable inside containers.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# I install dependencies first so Docker layer caching works better.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# I copy app source after dependencies to avoid reinstalls on code-only changes.
COPY . .

# I run Uvicorn on all interfaces so container port mapping works.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
