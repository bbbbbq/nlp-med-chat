#!/bin/bash
sudo rm -rf mysql_data
sudo docker-compose down
sudo docker-compose up -d
