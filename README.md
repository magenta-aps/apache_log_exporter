# Apache Log Exporter via Fluentd + Grok Exporter
[Prometheus](https://prometheus.io/) exporter for Apache Custom Logs,
implemented as [FluentD](https://www.fluentd.org/) and
[Grok Exporter](https://github.com/fstab/grok_exporter/) configurations.


To utilize the setup several steps must be taken:
1. Apache must be configured to output logs in the expected format.
2. FluentD must be configured to parse the log, and forward requests via http.
3. Grok Exporter must be configured to receive logs via http.

See `docker-compose.yml` for a full example.

## Apache Configuration
The setup needs a purpose built log file, which can be produced by entering
the following into apache2's configuration file:
```
LogFormat "{\"url\": \"%U\", \"method\": \"%m\", \"status\": %s, \"bytes_out\": %I, \"bytes_in\": %O, \"duration\": %D}" performance
CustomLog "logs/performance-app.log" performance
```
*Note: The usage of `%I`, `%O` and `%D` requires the logio module to be loaded*

## FluentD Configuration
FluentD needs to be configured to fetch the log lines from the above Apache 
server, parse them as JSON and then send them to the Grok Exporter.

A minimal example configuration can be found in `fluentd.conf`.

## Grok Exporter
The Grok Exporter needs to be receive requests via HTTP, and process them into
time-series metrics.

An example configuration equivalent to the previous `apache_log_exporter`
script can be found in `grok_exporter.conf`.

### Ceveats
There are the following ceveats compared to the `apache_log_exporter` script:
* `grok_exporter` does not mark collapsed metrics as DEAD upon removal.
* `grok_exporter` does not do regex replacement of URL elements such as UUIDs.

## Output
Navigating to the metrics url of `grok_exporter` (http://localhost:9144/metrics)
should produce output alike the following:
```
# HELP http_requests_total Number of requests processed.
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/media/UUID.jpg",status="206"} 14
http_requests_total{method="GET",path="/home/",status="200"} 31
...
# HELP http_latency_seconds Time taken to serve the request.
# TYPE http_latency_seconds histogram
http_latency_seconds_bucket{le="0.05",method="GET",path="/media/UUID.jpg",status="206"} 8.0
http_latency_seconds_bucket{le="0.1",method="GET",path="/media/UUID.jpg",status="206"} 9.0
http_latency_seconds_bucket{le="0.25",method="GET",path="/media/UUID.jpg",status="206"} 10.0
http_latency_seconds_bucket{le="0.5",method="GET",path="/media/UUID.jpg",status="206"} 11.0
http_latency_seconds_bucket{le="1.0",method="GET",path="/media/UUID.jpg",status="206"} 11.0
http_latency_seconds_bucket{le="2.5",method="GET",path="/media/UUID.jpg",status="206"} 13.0
http_latency_seconds_bucket{le="5.0",method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_latency_seconds_bucket{le="10.0",method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_latency_seconds_bucket{le="+Inf",method="GET",path="/media/UUID.jpg",status="206"} 14.0
...
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
# HELP http_received_bytes Bytes received, including request and headers.
# TYPE http_received_bytes histogram
http_received_bytes_bucket{le="1000.0",method="GET",path="/media/UUID.jpg",status="206"} 9.0
http_received_bytes_bucket{le="10000.0",method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_received_bytes_bucket{le="100000.0",method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_received_bytes_bucket{le="1e+06",method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_received_bytes_bucket{le="+Inf",method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_received_bytes_count{method="GET",path="/media/UUID.jpg",status="206"} 14.0
http_received_bytes_sum{method="GET",path="/media/UUID.jpg",status="206"} 12016.0
```
Along with the default entries for `grok_exporter`.

Thus the following metrics are provided:
* `http_requests_total` total number of requests processed.
* `http_latency_seconds` time spent serving requests.
* `http_sent_bytes` bytes sent serving requests.
* `http_received_bytes` bytes received serving requests.
