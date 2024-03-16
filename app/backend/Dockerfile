FROM python:3.11-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-postgres.sh /wait-for-postgres.sh
RUN chmod +x /wait-for-postgres.sh

COPY . .

EXPOSE 8000

CMD ["/wait-for-postgres.sh", "postgres", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
