FROM mcr.microsoft.com/vscode/devcontainers/python:3.13-bullseye

COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /usr/local/bin/

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
  && apt-get -y install --no-install-recommends git-flow \
  && rm -rf /var/lib/apt/lists/*

ENV TZ=Asia/Hong_Kong \
    UV_LINK_MODE=copy
