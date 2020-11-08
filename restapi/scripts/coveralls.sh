#!/usr/bin/env bash
docker-compose run -e COVERALLS_REPO_TOKEN=$(COVERALLS_REPO_TOKEN) -T backend coveralls
