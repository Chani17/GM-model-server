# Use the official python base image
FROM python:3.8

# Set the working directory inside the conatiner to /gm
WORKDIR /gm

# Copy only the necessary files for the requirements installation
COPY requirements.txt .

# Install necessary packages, avoiding the use of pip cache
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install torch torchvision torchaudio
RUN pip install uvicorn

# Copy all files from the current directory of the host machine into the /gm
COPY . .

# Run the application using Uvicorn with options for host, port, and automatic reload on code changes
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]