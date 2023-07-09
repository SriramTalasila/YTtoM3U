# Use the official Python image as the base image
FROM --platform=linux/arm64/v8 python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY . /app

# Install the dependencies
RUN pip install -r requirements.txt

# Expose the port that the Flask application will run on
EXPOSE 5000

# Start the Flask application
CMD python ./server.py
