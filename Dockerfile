# Official, lightweight Python Linux image
FROM python:3.10-slim-bullseye

#  Install the system tools needed to download the Microsoft Driver
RUN apt-get update && apt-get install -y curl gnupg2 unixodbc-dev apt-transport-https

# Inc. official Microsoft Repository for the ODBC Driver 18
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

#  Install the ODBC Driver 18 (Accepting the EULA automatically)
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Set up working directory inside the container
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python script into the container
COPY harvester.py .

# Run python script
CMD ["python", "harvester.py"]