#!/usr/bin/env bash
docker-compose run --rm test /bin/bash -c "black . && isort . && python -m unittest discover"