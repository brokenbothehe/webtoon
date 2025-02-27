# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create templates directory if it doesn't exist
RUN mkdir -p templates

# Add requests package (since it's used in the code but not in requirements.txt)

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "main.py"]
