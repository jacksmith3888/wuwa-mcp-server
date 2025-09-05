# Multi-stage Dockerfile optimized for uv and production deployment
FROM python:3.12-alpine as builder

# Install system dependencies for building
RUN apk add --no-cache gcc musl-dev linux-headers curl

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy Python project files
COPY pyproject.toml uv.lock README.md ./
COPY src ./src

# Install dependencies and build the package
RUN uv sync --frozen --no-dev --compile-bytecode

# Production stage
FROM python:3.12-alpine as production

# Install minimal runtime dependencies
RUN apk add --no-cache libgcc

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/

# Create app user for security
RUN addgroup -g 1000 appgroup && \
    adduser -D -u 1000 -G appgroup appuser

# Set working directory
WORKDIR /app

# Copy the built environment from builder stage
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Make sure the virtual environment is in PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Set environment variables for HTTP transport
ENV TRANSPORT=http
ENV PORT=8081
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Expose port 8081 for HTTP transport  
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the MCP server
CMD ["python", "-m", "wuwa_mcp_server.server"]
