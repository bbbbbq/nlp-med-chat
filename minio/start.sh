#!/bin/bash
sudo rm -rf minio_data
sudo docker-compose down
sudo docker-compose up -d
