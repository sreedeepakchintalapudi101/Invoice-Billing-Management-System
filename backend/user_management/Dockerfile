# # Base image
# FROM python:3.10-slim


# # Set work directory
# WORKDIR /app

# # Copy files
# # COPY . .
# COPY ../.. .

# # Install dependencies
# RUN pip install --no-cache-dir -r backend/user_management/requirements.txt

# ENV PYTHONPATH=/app

# RUN pip install flask_cors

# # Expose the port Flask runs on
# EXPOSE 8081

# # Run the app
# CMD ["python", "backend/user_management/user_management.py"]

# Use a stable Python base image
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Copy the project files into the container
# Since you're using `COPY ../.. .`, ensure this path is correct from your `Dockerfile` location.
COPY . .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r backend/user_management/requirements.txt

# Set PYTHONPATH to the app directory for imports
ENV PYTHONPATH=/app

# Install flask_cors if needed (already listed in requirements.txt?)
RUN pip install flask_cors

# Expose port 8081 (for Flask)
EXPOSE 8081

# Command to run the user management app
CMD ["python", "backend/user_management/user_management.py"]
