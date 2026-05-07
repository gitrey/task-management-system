# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port 8080
EXPOSE 8080

# Command to run the application
# Assuming uvicorn for a FastAPI/Starlette app as specified in specs
CMD exec uvicorn task_management.main:app --host 0.0.0.0 --port $PORT
