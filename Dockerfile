# Use the official python base image
FROM python:latest

# Set the working directory inside the conatiner to /gm
WORKDIR /gm

# Copy all files from the current directory of the host machine into the /gm
COPY . /gm

# Install necessary packages, avoiding the use of pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Run the application using Uvicorn with options for host, port, and automatic reload on code changes
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]