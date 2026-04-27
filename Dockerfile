FROM python:3.13.5-slim-bullseye

ENV TZ=Asia/Hong_Kong \
	UV_COMPILE_BYTECODE=1 \
	UV_LINK_MODE=copy \
	UV_PROJECT_ENVIRONMENT=/app/.venv \
	PATH="/app/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-dev

COPY . /app

CMD ["uv", "run", "main.py"]
