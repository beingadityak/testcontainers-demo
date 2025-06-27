# DNS Parser — Base64-Encoded DNS Query API

This is a production-ready Python Flask application that provides an HTTP API endpoint to decode and parse base64-encoded DNS queries (RFC 1035). It includes:

- A `/dns/queries` POST endpoint that returns parsed DNS questions and request ID.
- CLI tool to encode a domain as a DNS query and send to the server.
- Dockerized with minimal Alpine-based images and Gunicorn for WSGI.
- K8s manifests with health checks, CPU requests/limits, and Kustomize support.

## Features

- Parses DNS queries (base64, RFC1035)
- Returns request ID from DNS header
- Logs structured output with timestamps
- Flask server behind Gunicorn
- CLI to test endpoint easily
- Fully containerized, minimal image
- Kubernetes-ready with ingress + probes
- Easily override image tag & replicas via Kustomize

## How It Works

### POST `/dns/queries`

- Accepts a **base64-encoded DNS query** in the body.
- Parses the query and returns:
  ```json
  {
    "id": "query-id",
    "questions": [
      {
        "name": "www.google.com.",
        "type": "A"
      }
    ]
  }
  ```

- Response has caching headers: `ETag`, `Cache-Control`

## CLI Usage

### Pre-requisites
- Python 3.12+
- `click` library for CLI (install via `pip install click`)

### Run the CLI:

```bash
python client/cli.py www.google.com
```

### Example Output:

```bash
Status: 200
Headers:
  cache-control: public, max-age=3600
  etag: 3140f8...

Response:
{
  "id": "3140f8...",
  "questions": [
    {
      "name": "www.google.com.",
      "type": "A"
    }
  ]
}
```

You can also point to a remote server:

```bash
python client/cli.py www.google.com --url http://your-host/dns/queries
```

## Build and Run with Docker

### Build the image

```bash
docker build -t dns-parser-server -f Dockerfile.server .
```

### Run locally

```bash
docker run -p 5000:5000 dns-parser-server
```

## Deploy to Kubernetes

### Requirements

- Kubernetes cluster (minikube, EKS, GKE, etc.)
- `kubectl` and `kustomize` installed
- Ingress controller installed (e.g., nginx)

### Apply the manifests

```bash
kubectl apply -k k8s/overlays/prod
```

### Customize image tag or replicas

Edit `k8s/overlays/prod/kustomization.yaml`:

```yaml
images:
  - name: your-dockerhub-username/dns-parser-server
    newTag: v1.2.3

patchesStrategicMerge:
  - replica-patch.yaml
  - ingress-host-patch.yaml
```

Then re-apply:

```bash
kubectl apply -k k8s/overlays/prod
```

## Project Structure

```
dns_parser/
├── app/                  # Flask server logic
├── client/               # CLI client
├── tests/                # Unit tests
├── k8s/                  # Kubernetes manifests
│   ├── base/
│   └── overlays/prod/
├── Dockerfile.server     # Multi-stage, minimal server image
├── pyproject.toml        # Poetry config
├── run.py                # Entry point
└── README.md             # You're here
```

## Healthcheck Endpoints

The Flask server includes `/healthz` for liveness and readiness probes.