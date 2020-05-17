#!/bin/bash
cd "$(dirname "$0")"
RELEASE_CANDIDATE=1
VERSION_NUMBER=0.1.1
VERSION=master
TAG_PREFIX=
IMAGE=$(basename "$PWD")
IMAGE_PATH=${TAG_PREFIX}magentadk/${IMAGE}

# If release candidate, build and tag
if [ $RELEASE_CANDIDATE -eq 1 ]; then
    echo "Building docker container"
    docker build \
        --build-arg VERSION=${VERSION_NUMBER}rc \
        -t ${IMAGE_PATH}:latestrc $@ \
        .

    function tag {
        docker tag ${IMAGE_PATH}:latestrc ${IMAGE_PATH}:$1rc
        docker push ${IMAGE_PATH}:$1rc
    }

    IFS='.' read -ra VER <<< "${VERSION_NUMBER}"
    VER_SO_FAR="${VER[0]}"
    VER=("${VER[@]:1}")
    tag "$VER_SO_FAR"
    for i in "${VER[@]}"; do
        VER_SO_FAR=${VER_SO_FAR}.${i}
        tag "$VER_SO_FAR"
    done
    docker push ${IMAGE_PATH}:latestrc
else
    # If release, solely tag old release candidate
    function tag_release {
        docker tag ${IMAGE_PATH}:$1rc ${IMAGE_PATH}:$1
        docker push ${IMAGE_PATH}:$1
    }

    IFS='.' read -ra VER <<< "${VERSION_NUMBER}"
    VER_SO_FAR="${VER[0]}"
    VER=("${VER[@]:1}")
    tag_release "$VER_SO_FAR"
    for i in "${VER[@]}"; do
        VER_SO_FAR=${VER_SO_FAR}.${i}
        tag_release "$VER_SO_FAR"
    done
    docker tag ${IMAGE_PATH}:latestrc ${IMAGE_PATH}:latest
    docker push ${IMAGE_PATH}:latest
fi
