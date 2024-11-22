# Use a basic python image
FROM python:3.9-slim

# Establish working directory
WORKDIR /app

# Copy needed files
COPY app_files/ .

# Install requirements (For deploy use no cache dir, for development, dont use it)
#RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt
RUN pip install --disable-pip-version-check -r requirements.txt

# Expose port
EXPOSE 5000

# Execute the app
CMD ["python", "app.py"]