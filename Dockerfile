FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock /app/
COPY src /app/src

RUN uv sync --frozen

CMD ["uv", "run", "python", "-m", "wuwa_mcp_server.server"]
