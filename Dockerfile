# ------------------------------------------------------------------------------
# Stage 1: Build
# ------------------------------------------------------------------------------

FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder

# Set work directory
WORKDIR /app

# Create virtual environment
RUN uv venv

# Copy pyproject.toml
COPY pyproject.toml uv.lock .

# Install Python modules
RUN uv sync --no-cache --no-group dev

# ------------------------------------------------------------------------------
# Stage 2: Download Pandoc
# ------------------------------------------------------------------------------

FROM alpine:3.22 AS downloader

# Set Pandoc version at build time
ARG PANDOC_VERSION=3.8

# Fetch Pandoc executable from GitHub, decompress it, and make the binary
# executable
RUN apk add --no-cache curl tar \
    && curl -L https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux-amd64.tar.gz -o /tmp/pandoc.tar.gz \
    && tar -xzf /tmp/pandoc.tar.gz --strip-components=1 -C /usr/local/ \
    && chmod +x /usr/local/bin/pandoc

# ------------------------------------------------------------------------------
# Stage 3: Run
# ------------------------------------------------------------------------------

FROM python:3.13-alpine3.22 AS runner

# Set work directory
WORKDIR /app

# Copy venv from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy Pandoc binary from downloader stage
COPY --from=downloader /usr/local/bin/pandoc /usr/local/bin/pandoc

# Tell pypandoc where the pandoc executable is
ENV PYPANDOC_PANDOC=/usr/local/bin/pandoc

# Copy application code
COPY flaskr/ ./flaskr/

# Create a non-root user
RUN addgroup -S convert && adduser -S convert -G convert

# Ensure venv is used
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER convert

# Expose port 8080
EXPOSE 8080

# Run the server with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "flaskr:create_app()"]
