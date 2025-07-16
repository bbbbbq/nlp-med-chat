#!/bin/bash
rm -rf minio_data
docker-compose down
docker-compose up -d
