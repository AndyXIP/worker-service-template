#!/usr/bin/env bash
#MISE description="Build the Docker image"
docker build \
  --build-arg UV_VERSION="$(mise current uv)" \
  --build-arg PYTHON_VERSION="$(mise current python)" \
  -t api-service-template:latest .
