# Apache Custom Log Prometheus Exporter
[Prometheus](https://prometheus.io/) exporter for Apache Custom Logs.

## Running
```
python apache_log_exporter.py --file performance-app.log
```
Upon which a full smem default run will be printed, followed by:
```
Serving metrics on http://0.0.0.0:8452/metrics
```
The `performance-app.log` file can be produced by adding the following to Apache2:
```
CustomLog ${APACHE_LOG_DIR}/performance-app.log "%U %m %s %I %O %D"
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
* `http_update_time_seconds` unixtime of last log ingrestion.

## Usage
```
Usage: apache_log_exporter.py [OPTIONS]

Options:
  -f, --file TEXT                Logfile to open/follow.
  -o, --offset-file TEXT         File to store logfile offset.
  -u, --update-interval INTEGER  How often to ingest log content.
  -h, --host TEXT                Which host to run on.
  -p, --port INTEGER             Which port to run on.
  --help                         Show this message and exit.
```
