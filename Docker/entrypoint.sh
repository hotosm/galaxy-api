#!/bin/sh

echo ${GALAXY_API_CONFIG_FILE} | base64 -d | gzip -d | tee /app/src/config.txt
uvicorn API.main:app --reload --host 0.0.0.0 --port 8000
