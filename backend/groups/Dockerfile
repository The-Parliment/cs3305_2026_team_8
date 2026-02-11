                                                                                                                 FROM python:3.11-slim

WORKDIR /app

# Copy common module first (shared database code)
COPY common/ /app/common/

# Copy groups service requirements
COPY backend/groups/requirements.txt .

# Install Python dependencies (this will install common as editable package)
RUN pip install --no-cache-dir -r requirements.txt

# Copy groups service code
COPY backend/groups/ /app/

# Ensure /app is on import path
ENV PYTHONPATH=/app

# Expose port for groups service
EXPOSE 8003

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]

                                            
