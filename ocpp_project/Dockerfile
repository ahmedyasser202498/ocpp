# Dockerfile
FROM python:3.9-slim


# Set working directory
WORKDIR /app


# Install system dependencies including libpq-dev
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    redis-server \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the Django project code
COPY . /app/

# Expose the port the app will run on
EXPOSE 8000

# Set the environment variable for the settings module
ENV DJANGO_SETTINGS_MODULE=ocpp_project.settings

# Run migrations and then start the app using Daphne
CMD ["sh", "-c", "python manage.py migrate && python manage.py create_chargers && python manage.py create_user && uvicorn ocpp_project.asgi:application --host 0.0.0.0 --port 8000"]
