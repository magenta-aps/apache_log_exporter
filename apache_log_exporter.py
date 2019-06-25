import re
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

# TODO: Consider marking dead and ignored with specific labels for those purposes.
requests = Counter(
    'http_requests',
    'Number of requests processed.',
    ['method', 'path', 'status']
)
latency = Histogram(
    'http_latency',
    'Time taken to serve the request.',
    ['method', 'path', 'status'],
    unit='seconds',
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
label_update_time = Gauge(
    'http_label_update_time',
    'Time of a labelset was updated.',
    ['method', 'path', 'status'],
    unit='seconds',
)
update_time = Gauge(
    'http_update_time',
    'Time of last ingestion of log content.',
    unit='seconds',
)


uuid_regex = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.IGNORECASE)
number_regex = re.compile('\/[0-9]+\/')
# TODO: Optional path cleanup
def reduce_path(path, ignore_url_regexes):
    path = path.lower()
    path = uuid_regex.sub("UUID", path)
    path = number_regex.sub("/NUMBER/", path)
    for regex in ignore_url_regexes:
        if regex.search(path):
            return "IGNORED"
    return path


def parse_line(line, ignore_url_regexes):
    """Parse a single line / request from the log file.

    Apache entry:

        CustomLog ${APACHE_LOG_DIR}/performance-app.log "%U %m %s %I %O %D"
    """
    path, method, status, ibytes, obytes, duration = line.split()
    path = reduce_path(path, ignore_url_regexes)

    labels = {
        'path': path,
        'method': method,
        'status': status,
    }
    requests.labels(**labels).inc()
    bytes_received.labels(**labels).observe(float(ibytes))
    bytes_sent.labels(**labels).observe(float(obytes))
    latency.labels(**labels).observe(float(Decimal(duration) / 1000 / 1000))
    label_update_time.labels(**labels).set_to_current_time()


def update_readings(filename, offset_file, ignore_url_regexes):
    for line in Pygtail(filename, offset_file=offset_file):
        parse_line(line, ignore_url_regexes)
    update_time.set_to_current_time()


def collapse_metrics(collapse_time):
    if collapse_time == 0:
        return
    # Loop dict is required, as we change the dict while we iterate it.
    loop_dict = label_update_time._metrics.copy()
    for metric_tuple in loop_dict:
        # Dead entries cannot be eliminated
        if metric_tuple[1] == 'DEAD':
            continue
        # Check if we need to eliminate a series
        # TODO: Make time_since_last_update configurable, and WAY larger
        metric_update_time = label_update_time.labels(*metric_tuple)._value.get()
        time_since_last_update = time.time() - metric_update_time
        if time_since_last_update > collapse_time:
            print("Eliminating time series.", metric_tuple)
            labels = {
                'method': metric_tuple[0],
                'path': 'DEAD',
                'status': metric_tuple[2],
            }
            # Eliminate time series, by collapsing to DEAD series
            for metric in [requests, latency, bytes_sent, bytes_received, label_update_time]:
                entry = metric._metrics[metric_tuple]
                dead_entry = metric.labels(**labels)
                del metric._metrics[metric_tuple]
                if isinstance(entry, Counter) or isinstance(entry, Gauge):
                    eliminate_value = entry._value.get()
                    old_value = metric.labels(**labels)._value.get()
                    dead_entry._value.set(old_value + eliminate_value)
                elif isinstance(entry, Histogram):
                    eliminate_sum = entry._sum.get()
                    old_sum = metric.labels(**labels)._sum.get()
                    dead_entry._sum.set(old_sum + eliminate_sum)
                    # NOTE: We assume bounds match, they should.
                    # TODO: Assert that it is true.
                    for i, bound in enumerate(entry._upper_bounds):
                        eliminate_buck = entry._buckets[i].get()
                        old_buck = metric.labels(**labels)._buckets[i].get()
                        dead_entry._buckets[i].set(old_buck + eliminate_buck)
                else:
                    print("Unhandled series type")


@click.command()
@click.option('-f', '--file', 'filename', help='Logfile to open/follow.', prompt=True)
@click.option('-o', '--offset-file', default="offset.file", help='File to store logfile offset. (default=offset.file)')
@click.option('-u', '--update-interval', default=10, help='How often to ingest log content. (default=10)')
@click.option('-h', '--host', default='0.0.0.0', help='Which host to run on. (default=0.0.0.0)')
@click.option('-p', '--port', default=8452, help='Which port to run on. (default=8452)')
@click.option('-c', '--collapse-time', default=0, help='Interval for collapsing metrics. (default=off)')
@click.option('-i', '--ignore-url', 'ignore_urls', help='URL to ignore (regex).', multiple=True)
def launch(filename, offset_file, update_interval, host, port, ignore_urls, collapse_time):
    # Compile ignore_url regexes
    ignore_url_regexes = [re.compile(ignore_url) for ignore_url in ignore_urls]
    # Pre-populate our metrics
    update_readings(filename, offset_file, ignore_url_regexes)
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
            update_readings(filename, offset_file, ignore_url_regexes)
            collapse_metrics(collapse_time)
            last = time.time()


if __name__ == '__main__':
    launch()
