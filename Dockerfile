FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the root of the project as the working directory
WORKDIR /workspace

# Install dependencies first to leverage Docker layer caching
COPY app/requirements.txt ./app/
RUN pip install --no-cache-dir -r app/requirements.txt gunicorn

# Copy application source code
COPY app/ ./app/

# Expose standard Flask port
EXPOSE 5000

# Execute the application via Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--reload", "app.main:app"]