FROM python:3.11 AS builder
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock README.md ./

# Install only dependencies, not the package itself
RUN uv sync --no-dev --no-install-project

FROM python:3.11-slim
WORKDIR /app

# Copy the virtual environment from builder stage
COPY --from=builder /app/.venv .venv/

# Copy application code
COPY . .

# Run the application directly with Python
CMD ["/app/.venv/bin/python", "-m", "flask", "--app", "bluesky_summarizer", "run", "--host=0.0.0.0", "--port=8080"]

