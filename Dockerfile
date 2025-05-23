# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY src/. /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r dependencies.txt

# Make port 8080 available to the world outside this container

# Run app.py when the container launches
CMD ["uvicorn", "app:app", "--reload", "--reload-include", "*.yaml", "--port", "8085", "--host", "0.0.0.0"]
