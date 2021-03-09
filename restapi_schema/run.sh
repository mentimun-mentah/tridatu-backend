#!/bin/bash
mkdir -m 777 output; docker-compose up --build; docker-compose down; docker rmi schemaspy/schemaspy:snapshot; docker rmi nginx:stable-alpine; rm -rf output
