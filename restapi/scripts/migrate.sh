#!/usr/bin/env bash
docker-compose exec -T backend /bin/bash -c 'mkdir alembic/versions'
docker-compose exec -T backend /bin/bash -c 'alembic revision --autogenerate -m "init db"; alembic upgrade head'
docker-compose exec -T backend /bin/bash -c 'rm -rf alembic/versions'

docker-compose exec postgres psql -U tridatu -c "COPY provinces (name,code) FROM '/home/provinces.csv' delimiter ',' csv header;"
docker-compose exec postgres psql -U tridatu -c "COPY postal_codes (urban,sub_district,city,postal_code,province_code) FROM '/home/postal_codes.csv' delimiter ',' csv header;"
