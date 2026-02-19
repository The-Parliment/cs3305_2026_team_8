FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy auth service code (main.py, settings.py, security.py, structures.py, etc.)
COPY . .

# Ensure /app is on import path so /app/common (volume) can be imported
ENV PYTHONPATH=/app

EXPOSE 8005
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]