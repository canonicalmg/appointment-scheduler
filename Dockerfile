# Use the official Python image as the base image
FROM python:3.11.3

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project files
COPY . .
COPY .env .env
COPY .bashrc /root/

# Expose the port the app will run on
EXPOSE 8000

# Start the Django development server
CMD ["bash", "-i", "-c", "python manage.py runserver 0.0.0.0:8000"]

