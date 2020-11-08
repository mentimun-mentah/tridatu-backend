#!/usr/bin/env bash
docker-compose exec -e COVERALLS_REPO_TOKEN="$GITHUB_TOKEN" -T backend coveralls
