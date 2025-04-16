# Stage 1: Build dependencies
FROM python:3.13.0-alpine3.19 AS builder

WORKDIR /app

# Install build dependencies
RUN apk update && apk upgrade --no-cache && \
    apk add --no-cache \
    gcc \
    musl-dev \
    curl

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Production image
FROM python:3.13.0-alpine3.19

WORKDIR /app

# Install runtime dependencies
RUN apk update && apk upgrade --no-cache && \
    apk add --no-cache \
    curl

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install application dependencies
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 