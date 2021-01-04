#!/usr/bin/env bash
docker-compose exec -T backend /bin/bash -c 'mkdir alembic/versions'
docker-compose exec -T backend /bin/bash -c 'alembic revision --autogenerate -m "init db"; alembic upgrade head'
docker-compose exec -T backend /bin/bash -c 'rm -rf alembic/versions'

docker-compose exec -T postgres psql -U tridatu -c "COPY provinces (name,code) FROM '/home/provinces.csv' delimiter ',' csv header;"
docker-compose exec -T postgres psql -U tridatu -c "COPY postal_codes (urban,sub_district,city,postal_code,province_code) FROM '/home/postal_codes.csv' delimiter ',' csv header;"
docker-compose exec -T postgres psql -U tridatu -c "COPY shipping_provinces (id,name) FROM '/home/shipping_provinces.csv' delimiter ',' csv header;"
docker-compose exec -T postgres psql -U tridatu -c "COPY shipping_cities (id,name,type,shipping_province_id) FROM '/home/shipping_cities.csv' delimiter ',' csv header;"
docker-compose exec -T postgres psql -U tridatu -c "COPY shipping_subdistricts (id,name,shipping_city_id) FROM '/home/shipping_subdistricts.csv' delimiter ',' csv header;"
