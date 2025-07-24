# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files into container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask's default port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
