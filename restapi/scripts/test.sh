#!/usr/bin/env bash
docker-compose exec -T backend pytest --cov=tests --cov-report=term-missing --cov-report=html -v -s
