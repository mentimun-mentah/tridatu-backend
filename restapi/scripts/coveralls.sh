#!/usr/bin/env bash
docker-compose run -e COVERALLS_REPO_TOKEN=${{ secrets.GITHUB_TOKEN }} -T backend coveralls
