FROM python:3
ARG VERSION
ENV VERSION=${VERSION}

WORKDIR /app

RUN groupadd -r apachelogexporter --gid=999
RUN useradd -m -r -g apachelogexporter --uid=999 apachelogexporter
USER apachelogexporter

COPY requirements.txt .
RUN pip install --user -r requirements.txt --no-cache-dir

COPY . .

USER root
RUN chown -R apachelogexporter:apachelogexporter /app
USER apachelogexporter

ENTRYPOINT /app/apache_log_exporter.py
