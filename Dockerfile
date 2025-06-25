# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables that prevent Python from writing .pyc files to disc and buffering output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /usr/src/app

# Install dependencies from requirements.txt
# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend directory which will contain the Django project
COPY ./backend /usr/src/app/backend

# Set the working directory to the backend folder
WORKDIR /usr/src/app/backend 