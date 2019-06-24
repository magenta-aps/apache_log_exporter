import time
import datetime
from decimal import Decimal

import click
from pygtail import Pygtail

from prometheus_client.utils import INF
from prometheus_client import (
    Histogram,
    Counter,
    Gauge,
    make_wsgi_app,
)
from wsgiref.simple_server import make_server

requests = Counter(
    'http_requests',
    'Number of requests processed.',
    ['method', 'path', 'status']
)
latency = Histogram(
    'http_latency',
    'Time taken to serve the request.',
    ['method', 'path', 'status'],
    unit='microseconds',
)
byte_buckets=[10 ** x for x in range(3,7,1)] + [INF]
bytes_sent = Histogram(
    'http_sent_bytes',
    'Bytes sent, including headers.',
    ['method', 'path', 'status'],
    unit='bytes',
    buckets=byte_buckets,
)
bytes_received = Histogram(
    'http_received_bytes',
    'Bytes received, including request and headers.',
    ['method', 'path', 'status'],
    unit='bytes',
    buckets=byte_buckets,
)
update_time = Gauge(
    'http_update_time',
    'Time of last ingestion of log content.',
    unit='seconds',
)


def parse_line(line):
    """Parse a single line / request from the log file.

    Apache entry:

        CustomLog ${APACHE_LOG_DIR}/performance-app.log "%U %m %s %I %O %D"
    """
    path, method, status, ibytes, obytes, time = line.split()
    labels = {
        'path': path,
        'method': method,
        'status': status,
    }
    requests.labels(**labels).inc()
    bytes_received.labels(**labels).observe(float(ibytes))
    bytes_sent.labels(**labels).observe(float(obytes))
    latency.labels(**labels).observe(float(Decimal(time) / 1000 / 1000))


def update_readings(filename):
    for line in Pygtail(filename):
        parse_line(line)
    update_time.set(time.time())


@click.command()
@click.option('-f', '--file', help='Logfile to open/follow.', prompt=True)
@click.option('-o', '--offset-file', default="offset.file", help='File to store logfile offset.')
@click.option('-u', '--update-interval', default=10, help='How often to ingest log content.')
@click.option('-h', '--host', default='0.0.0.0', help='Which host to run on.')
@click.option('-p', '--port', default=8452, help='Which port to run on.')
def launch(filename, update_interval, host, port):
    # Pre-populate our metrics
    update_readings(filename)
    # Start WSGI server
    app = make_wsgi_app()
    httpd = make_server(host, port, app)
    print("Serving metrics on http://" + host + ":" + str(port) + "/metrics")
    # Start handling requests, timing out every update_interval to update readings.
    last = time.time()
    while True:
        # Timeout every second, to check if we need to update readings.
        httpd.timeout = 1
        httpd.handle_request()
        now = time.time()
        # Only update every 'update_interval' seconds
        if now - last > update_interval:
            update_readings(filename)
            last = time.time()


if __name__ == '__main__':
    launch()
