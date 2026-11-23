FROM ghcr.io/astral-sh/uv:python3.12-alpine AS build

ENV UV_COMPILE_BYTECODE=1 \
	UV_NO_DEV=1 \
	UV_TOOL_BIN_DIR=/usr/local/bin \
	UV_LINK_MODE=copy \
	UV_PYTHON_DOWNLOADS=never 

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
	--mount=type=bind,source=uv.lock,target=/app/uv.lock \
	--mount=type=bind,source=pyproject.toml,target=/app/pyproject.toml \
	uv sync --locked --no-install-project --no-editable

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
	uv sync --locked --no-editable

FROM python:3.12-alpine

RUN addgroup -S -g 1001 unprivileged \
 && adduser -S -u 1001 -G unprivileged unprivileged

WORKDIR /app
ENV PYTHONBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1 \
	PATH="/app/.venv/bin:$PATH"

COPY --from=build --chown=unprivileged:unprivileged /app/.venv /app/.venv
COPY --chown=unprivileged:unprivileged . /app

ENTRYPOINT []
USER unprivileged
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]

