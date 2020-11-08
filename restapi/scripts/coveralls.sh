#!/usr/bin/env bash
docker-compose run -e GITHUB_TOKEN=$secrets.GITHUB_TOKEN -T backend coveralls
