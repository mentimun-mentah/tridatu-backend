#!/bin/bash
set -e

if [ "$1" = 'production' ]; then
  uvicorn app:app --host 0.0.0.0 --proxy-headers
else
  uvicorn app:app --host 0.0.0.0 --proxy-headers --reload
fi
