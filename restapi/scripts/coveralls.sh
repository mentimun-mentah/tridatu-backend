#!/usr/bin/env bash
docker-compose run --env GITHUB_TOKEN=$secrets.GITHUB_TOKEN backend coveralls
