FROM python:3.12-alpine AS builder

# System dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev

# Create working directory
WORKDIR /app

# Install Poetry
ENV POETRY_VERSION=1.8.2
RUN pip install "poetry==$POETRY_VERSION"

# Copy and export dependencies
COPY pyproject.toml poetry.lock* ./
RUN poetry export --without-hashes --format=requirements.txt > requirements.txt


FROM python:3.12-alpine

# Add runtime dependencies
RUN apk add --no-cache libffi curl

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set work directory and permissions
WORKDIR /app
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Change ownership
RUN chown -R appuser:appgroup /app

# Use non-root user
USER appuser

# Expose port
EXPOSE 5000

# Entrypoint with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
