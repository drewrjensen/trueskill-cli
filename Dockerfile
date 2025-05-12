# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Pipfile and Pipfile.lock to the container
COPY Pipfile Pipfile.lock /app/

# Install dependencies
RUN pip install pipenv && pipenv install --system --deploy

# Install PyInstaller for building the app into a Linux executable
RUN pip install pyinstaller

# Install binutils to provide objdump, required by PyInstaller on Linux
RUN apt-get update && apt-get install -y binutils && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code to the container
COPY . /app

# Explicitly copy schemas.sql to the /app directory
COPY schemas.sql /app/

# Explicitly copy clean.sh to the /app directory
COPY clean.sh /app/

# Build the application into a Linux executable
RUN pyinstaller --onefile --add-data "schemas.sql:." src/main.py

# Move the built executable to the root directory and rename it to 'main'
RUN mv dist/main /app/main

# Run the clean.sh script to clean up build artifacts
RUN chmod +x clean.sh && ./clean.sh

# Expose the port the app runs on (if applicable)
EXPOSE 8000

# Define the command to run the application
CMD ["python", "src/main.py"]
