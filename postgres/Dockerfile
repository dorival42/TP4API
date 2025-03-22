FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy import script and models
COPY init/ /app/init/

# Set working directory to init folder where models.py is located
WORKDIR /app/init

# Run import script
CMD ["python", "import_data.py"]
