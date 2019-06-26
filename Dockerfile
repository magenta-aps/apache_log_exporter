FROM python:3
ARG VERSION
ENV VERSION=${VERSION}

WORKDIR /app

COPY requirements.txt .
RUN pip install --user -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT /app/apache_log_exporter.py
