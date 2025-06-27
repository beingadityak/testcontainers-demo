# DNS Parser API

A Flask-based HTTP API that accepts base64-encoded DNS queries (RFC1035), decodes and parses them, logs request/response, and returns DNS questions and answers in JSON. It includes rate-limiting via Redis and DNS resolution fallback to local and public resolvers.

---

## 🚀 Features

- Accepts base64-encoded DNS queries via `POST /dns/queries`
- Parses multiple DNS questions (RFC1035)
- Returns JSON with ID, questions, and DNS answers
- Performs DNS resolution with local and fallback resolvers
- Implements IP-based rate limiting using Redis
- Returns `429 Too Many Requests` with `Retry-After` header
- Supports caching with `ETag` and `If-None-Match`
- Exposes health check at `/healthz`

---

## 🗂 Project Structure

```
dns_parser/
├── dns_querier/      # Flask app logic
├── client/           # CLI tool to send DNS queries
├── e2e/              # End-to-end tests using testcontainers
├── tests/            # Unit tests
├── Dockerfile.server # Multi-stage minimal server image
├── docker-compose.yml
├── pyproject.toml
├── README.md
```

---

## 🧪 Test Suite with TestContainers

This project uses [`testcontainers`](https://github.com/testcontainers/testcontainers-python) to run integration and e2e tests in isolated Docker-based environments.

### ✅ Install dependencies:

```bash
poetry install
```

### ▶️ Run all tests:

```bash
poetry run pytest
```

This will automatically spin up a Redis container for rate-limiting tests.

---

## 🖥 Running the Server Locally

### Using Poetry:

```bash
poetry run python run.py
```

### Or using Docker:

```bash
docker build -f Dockerfile.server -t dns-parser-server .
docker run -p 5000:5000 dns-parser-server
```

Health check:

```bash
curl http://localhost:5000/healthz
```

---

## 🧰 Using the CLI

The project includes a simple CLI tool to send DNS queries:

```bash
poetry run python client/cli.py www.google.com
```

You can change the endpoint URL using:

```bash
poetry run python client/cli.py www.google.com --url http://localhost:5000/dns/queries
```

---

## 📂 GitHub Actions

- All tests are run via CI using `pytest`
- Docker image builds are only triggered **if tests pass**
- Separate workflows are used for test and image build stages

---

## 📝 License

MIT
