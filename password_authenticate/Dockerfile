FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py keygen.py ./

# Expose the port (FastAPI default is 8000)
EXPOSE 8000

# Set environment variable for the password
ENV EXPECTED_PASSWORD=supersecret

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
