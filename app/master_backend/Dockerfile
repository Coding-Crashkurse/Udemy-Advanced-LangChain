FROM python:3.11-slim

WORKDIR /usr/src/app

# Update apt-get and install necessary packages including postgresql-client and g++
RUN apt-get update && \
    apt-get install -y postgresql-client g++ && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir --default-timeout=600 -r requirements.txt


COPY wait-for-postgres.sh /wait-for-postgres.sh
RUN chmod +x /wait-for-postgres.sh

COPY . .

EXPOSE 8000

CMD ["/wait-for-postgres.sh", "postgres", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
