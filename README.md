# Apache Custom Log Prometheus Exporter
[Prometheus](https://prometheus.io/) exporter for Apache Custom Logs.

## Running
The program needs access to a purpose built log file, which can be produced by
entering the following into apache2's configuration file:
```
CustomLog ${APACHE_LOG_DIR}/performance-app.log "%U %m %s %I %O %D"
```
The log will then be exported to `/var/log/apache2/performance-app.log` by default.

At which point we are ready to start the program
### Via docker
```
docker run -d -p 8452:8452 -v /var/log/apache2:/srv/
    -e APACHE_LOG_EXPORTER_FILENAME=/srv/performance-app.log
    skeen/apache_log_exporter:latestrc
```

### Natively
```
python apache_log_exporter.py --file performance-app.log
```

### Via Apaches CustomLog
The CustomLog line from above can be changed to pipe the output directly into a
process, and thus eliminating the need for a seperate file:
```
CustomLog "|/app/apache_log_exporter.py -f-" "%U %m %s %I %O %D"
```
NOTE: This does not work right now.

## How does the programw work
When the program starts, it will run a full scan of the log file, followed by:
```
Serving metrics on http://0.0.0.0:8452/metrics
```
Being print to the console, at this point metrics should be available and the log
should be ingested at regular intervals.

Each line of the log-file corresponds to a single HTTP request, and these lines
are processed and exported to combined metrics. See the `Output` section below
for a list of the exported metrics.

See the `Usage` section below for configuration and variables.

## Usage
```
Usage: apache_log_exporter.py [OPTIONS]

Options:
  -f, --file TEXT                Logfile to open/follow.
  -o, --offset-file TEXT         File to store logfile offset.
                                 (default=offset.file)
  -u, --update-interval INTEGER  How often to ingest log content. (default=10)
  -h, --host TEXT                Which host to run on. (default=0.0.0.0)
  -p, --port INTEGER             Which port to run on. (default=8452)
  -c, --collapse-time INTEGER    Interval for collapsing metrics.
                                 (default=off)
  -i, --ignore-url TEXT          URL to ignore (regex).
  --help                         Show this message and exit.
```
Note: All of these can also be provided via environmental variables:
```
APACHE_LOG_EXPORTER_FILENAME=/var/log/apache2/performance.log
APACHE_LOG_EXPORTER_OFFSET_FILENAME=offset.file
APACHE_LOG_EXPORTER_UPDATE_INTERVAL=10
APACHE_LOG_EXPORTER_HOST=127.0.0.1
APACHE_LOG_EXPORTER_PORT=1337
APACHE_LOG_EXPORTER_COLLAPSE_TIME=43200
APACHE_LOG_EXPORTER_IGNORE_URL=/static/:/media/
```

## Output
Navigating to the metrics url, should produce output alike the following:
```
# HELP http_requests_total Number of requests processed.
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_requests_total{method="GET",path="/home/",status="200"} 31.0
...
# TYPE http_requests_created gauge
http_requests_created{method="GET",path="/media/UUID.jpg",status="206"} 1.5613879602692363e+09
http_requests_created{method="GET",path="/home/",status="200"} 1.5613879602695909e+09
...
# HELP http_latency_seconds Time taken to serve the request.
# TYPE http_latency_seconds histogram
http_latency_seconds_bucket{le="0.005",method="GET",path="/media/UUID.jpg",status="206"} 8.0
http_latency_seconds_bucket{le="0.01",method="GET",path="/media/UUID.jpg",status="206"} 8.0
http_latency_seconds_bucket{le="0.025",method="GET",path="/media/UUID.jpg",status="206"} 8.0
http_latency_seconds_bucket{le="0.05",method="GET",path="/media/UUID.jpg",status="206"} 8.0
http_latency_seconds_bucket{le="0.075",method="GET",path="/media/UUID.jpg",status="206"} 8.0
http_latency_seconds_bucket{le="0.1",method="GET",path="/media/UUID.jpg",status="206"} 9.0
http_latency_seconds_bucket{le="0.25",method="GET",path="/media/UUID.jpg",status="206"} 10.0
http_latency_seconds_bucket{le="0.5",method="GET",path="/media/UUID.jpg",status="206"} 11.0
http_latency_seconds_bucket{le="0.75",method="GET",path="/media/UUID.jpg",status="206"} 11.0
http_latency_seconds_bucket{le="1.0",method="GET",path="/media/UUID.jpg",status="206"} 11.0
http_latency_seconds_bucket{le="2.5",method="GET",path="/media/UUID.jpg",status="206"} 13.0
http_latency_seconds_bucket{le="5.0",method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_latency_seconds_bucket{le="7.5",method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_latency_seconds_bucket{le="10.0",method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_latency_seconds_bucket{le="+Inf",method="GET",path="/media/UUID.jpg",status="206"} 14.0
...
# TYPE http_latency_seconds_created gauge
http_latency_seconds_created{method="GET",path="/media/UUID.jpg",status="206"} 1.5613879602693326e+09
http_latency_seconds_created{method="GET",path="/home/",status="200"} 1.5613879602696514e+09
...
# HELP http_sent_bytes Bytes sent, including headers.
# TYPE http_sent_bytes histogram
http_sent_bytes_bucket{le="1000.0",method="GET",path="/media/UUID.jpg",status="206"} 3.0
http_sent_bytes_bucket{le="10000.0",method="GET",path="/media/UUID.jpg",status="206"} 7.0
http_sent_bytes_bucket{le="100000.0",method="GET",path="/media/UUID.jpg",status="206"} 9.0
http_sent_bytes_bucket{le="1e+06",method="GET",path="/media/UUID.jpg",status="206"} 13.0
http_sent_bytes_bucket{le="+Inf",method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_sent_bytes_count{method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_sent_bytes_sum{method="GET",path="/media/UUID.jpg",status="206"} 2.255652e+06
...
# TYPE http_sent_bytes_created gauge
http_sent_bytes_created{method="GET",path="/media/UUID.jpg",status="206"} 1.5613879602693017e+09
http_sent_bytes_created{method="GET",path="/home/",status="200"} 1.5613879602696295e+09
...
# HELP http_received_bytes Bytes received, including request and headers.
# TYPE http_received_bytes histogram
http_received_bytes_bucket{le="1000.0",method="GET",path="/media/UUID.jpg",status="206"} 9.0
http_received_bytes_bucket{le="10000.0",method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_received_bytes_bucket{le="100000.0",method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_received_bytes_bucket{le="1e+06",method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_received_bytes_bucket{le="+Inf",method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_received_bytes_count{method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_received_bytes_sum{method="GET",path="/media/UUID.jpg",status="206"} 12016.0
...
# TYPE http_received_bytes_created gauge
http_received_bytes_created{method="GET",path="/media/UUID.jpg",status="206"} 1.561387960269257e+09
http_received_bytes_created{method="GET",path="/home/",status="200"} 1.561387960269603e+09
...
# HELP http_label_update_time_seconds Time of a labelset was updated.
# TYPE http_label_update_time_seconds gauge
http_label_update_time_seconds{method="GET",path="/media/UUID.jpg",status="206"} 1.5613879603086698e+09
http_label_update_time_seconds{method="GET",path="/home/",status="200"} 1.5613879603086698e+09
...
# HELP http_update_time_seconds Time of last ingestion of log content.
# TYPE http_update_time_seconds gauge
http_update_time_seconds 1.5613879603086698e+09
```
Along with the default entries for `python` and `process`.

Thus the following metrics are provided:
* `http_requests_total` total number of requests processed.
* `http_latency_seconds` time spent serving requests.
* `http_sent_bytes` bytes sent serving requests.
* `http_received_bytes` bytes received serving requests.
* `http_label_update_time_seconds` unixtime of last label update.
* `http_update_time_seconds` unixtime of last log ingrestion.
```
