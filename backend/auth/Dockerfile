FROM python:3.11-slim
WORKDIR /app
COPY  auth/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Remove the ../ - just use database
COPY database /app/database

# This will work if context is project root
COPY auth /app/auth

ENV PYTHONPATH=/app

CMD ["uvicorn", "auth.main:app", "--host", "0.0.0.0", "--port", "8000"]
