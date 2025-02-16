FROM python:3.11.5-slim

# Set the working directory
WORKDIR /opt/app

# Copy the application code
COPY ./requirements.txt /opt/requirements.txt
COPY ./app /opt/app

# Install dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /opt/requirements.txt