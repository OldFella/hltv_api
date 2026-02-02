# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app/src

# Copy requirements first (for caching)
COPY ./requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY src/ .

# Expose port FastAPI will run on
EXPOSE 8000

# Run the app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
