FROM python:3.11
ENV TZ=America/Argentina/Mendoza
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

COPY ./requirements.txt .
COPY ./uwsgi.ini .

# Install prerequisites and add GPG keys
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ftp-master.debian.org/keys/archive-key-12.asc | gpg --dearmor -o /usr/share/keyrings/debian-archive-keyring.gpg && \
    curl -fsSL https://ftp-master.debian.org/keys/archive-key-12-security.asc | gpg --dearmor -o /usr/share/keyrings/debian-security-keyring.gpg

# Configure APT sources to use the imported keyrings
RUN echo "deb [signed-by=/usr/share/keyrings/debian-archive-keyring.gpg] http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list.d/debian.list && \
    echo "deb [signed-by=/usr/share/keyrings/debian-security-keyring.gpg] http://deb.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list.d/debian.list && \
    echo "deb [signed-by=/usr/share/keyrings/debian-archive-keyring.gpg] http://deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list.d/debian.list

# Update APT and install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    uwsgi-plugin-python3 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up application directory
RUN mkdir -p /app/tmp

# Upgrade pip and install Python dependencies
RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY code/ .

# Define the entrypoint for the container
CMD ["uwsgi","--wsgi-file","main.py","--ini","uwsgi.ini"]
