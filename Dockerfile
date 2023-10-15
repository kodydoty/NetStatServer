# Use the official Python 3.11 image as the base image
FROM python:3.11

# Set environment variables
ENV DATABASE_URL "postgresql+asyncpg://pgusername:pgpassword@postgres:5432/databasename"

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the application code into the container
COPY app /app

# Expose the port your FastAPI app will run on
EXPOSE 80

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
