FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

RUN groupadd --system --gid 999 unprivileged \
 && useradd --system --gid 999 --uid 999 --create-home unprivileged

WORKDIR /app

ENV PYTHONBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_DEV=1
ENV UV_TOOL_BIN_DIR=/usr/local/bin

COPY pyproject.toml uv.lock /app
RUN uv sync --locked --no-install-project

COPY . /app
RUN uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT []
USER unprivileged
EXPOSE 8000
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]