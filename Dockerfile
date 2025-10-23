# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Pygame might use (if any, though usually not for desktop games)
# For Pygame, this is often not necessary as it creates its own window.
# If you were running a web server or similar, you would expose a port.
# EXPOSE 8000

# Run main.py when the container launches
CMD ["python", "main.py"]
