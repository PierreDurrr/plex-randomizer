# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Install required dependencies
RUN apt-get update && apt-get install -y curl nano

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Run script.py when the container launches
#CMD ["sh", "-c", "service cron start && python3 /app/scripts/cron_helper.py"]
#CMD ["python3", "/app/scripts/cron_helper.py"]

# Copy crontab file
#COPY crontab /etc/crontabs/root
# Adding crontab to the appropriate location
ENV PYTHONUNBUFFERED 1

COPY crontab /etc/crontabs/root
# imports crontab
RUN crontab /etc/crontabs/root

CMD ["sh", "-c", "cron -f -l 2 && echo 'Container is running. Waiting for next run.'"]
 
# Define the volume
#VOLUME /config
