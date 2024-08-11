FROM python:3.11-slim

WORKDIR /usr/src/app

# Update apt-get and install necessary packages including postgresql-client, g++, and dos2unix
RUN apt-get update && \
    apt-get install -y postgresql-client g++ dos2unix && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# Install PyTorch and other Python dependencies
RUN pip install --no-cache-dir --default-timeout=600 -r requirements.txt

COPY wait-for-postgres.sh /wait-for-postgres.sh

# Convert wait-for-postgres.sh to Unix line endings and make it executable
RUN dos2unix /wait-for-postgres.sh && chmod +x /wait-for-postgres.sh

COPY . .

EXPOSE 8000

CMD ["/wait-for-postgres.sh", "postgres", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
