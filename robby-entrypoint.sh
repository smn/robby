#!/bin/bash -e

echo "Starting robby with redis://${REDIS_HOST:-127.0.0.1}:${REDIS_PORT:-6379}/${REDIS_DB:-1}"
python `which robby` \
    --redis-uri redis://${REDIS_HOST:-127.0.0.1}:${REDIS_PORT:-6379}/${REDIS_DB:-1} \
    --interface 0.0.0.0 \
    --port ${ROBBY_PORT:-8080} \
    --prefix ${ROBBY_PREFIX:-"robby"} \
    --debug
