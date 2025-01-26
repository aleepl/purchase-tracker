FROM python:3.11.5-slim

# Set the working directory
WORKDIR /opt/app

# Copy requirements file and install dependencies
COPY ./requirements.txt /opt/app/

# Install dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app /opt/app
COPY ./main.py /opt/
