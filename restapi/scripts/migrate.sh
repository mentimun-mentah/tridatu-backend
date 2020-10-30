#!/usr/bin/env bash

docker-compose exec backend /bin/bash -c 'alembic revision --autogenerate -m "init db"; alembic upgrade head'
