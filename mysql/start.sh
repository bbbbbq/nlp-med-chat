#!/bin/bash
rm -rf mysql_data
docker-compose down
docker-compose up -d
