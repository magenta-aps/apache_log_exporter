# This image has been build to 
# image: magentaaps/grok_exporter:latest-rc
#
# usage instructions:
# docker build -f grok_exporter.Dockerfile -t magentaaps/grok_exporter:latest-rc .
#############################
# Multi-Stage Build

FROM golang:stretch as builder
ENV GITHUB_REPOSITORY=github.com/fstab/grok_exporter

# Install system deps
#   We need this in order to build oniguruma.
#   The debian deb packages for onigurma do not install static libs
RUN apt-get update && apt-get -y install build-essential make autoconf libtool

# Oniguruma: fetch, build, and install static libs
RUN cd /tmp && \
    git clone https://github.com/kkos/oniguruma.git && \
    cd /tmp/oniguruma && \
    autoreconf -vfi && \
    ./configure && \
    make && \
    make install

# grok_exporter: fetch source code
RUN mkdir -p /go/src/$GITHUB_REPOSITORY
RUN git clone https://$GITHUB_REPOSITORY.git /go/src/$GITHUB_REPOSITORY

# Fetch Golang Dependencies
WORKDIR /go/src/$GITHUB_REPOSITORY
RUN git submodule update --init --recursive
RUN go get

# Build Statically-Linked Binary
RUN GOOS=linux GOARCH=amd64 CGO_ENABLED=1 go build \
    -ldflags "-w -extldflags \"-static\" \
    -X ./exporter.Version=$VERSION \
    -X ./exporter.BuildDate=$(date +%Y-%m-%d) \
    -X ./exporter.Branch=$(git rev-parse --abbrev-ref HEAD) \
    -X ./exporter.Revision=$(git rev-parse --short HEAD) \
    "

RUN cp /go/src/$GITHUB_REPOSITORY/grok_exporter /srv/grok_exporter
RUN cp -r /go/src/$GITHUB_REPOSITORY/logstash-patterns-core /srv/logstash-patterns-core

#############################
# Final-Stage Build

FROM alpine:latest

WORKDIR /app

COPY --from=builder /srv/grok_exporter /app/grok_exporter
COPY --from=builder /srv/logstash-patterns-core /app/logstash-patterns-core

EXPOSE 9144
ENTRYPOINT [ "/app/grok_exporter" ]
