import logging
import os
import redis
from flask import Flask, request, jsonify, make_response
from dnslib import DNSRecord

from dns_querier.utils import decode_and_parse_dns_query
from dns_querier.resolver import resolve_dns_query

def parse_request_id(dns_bytes: bytes) -> str:
    """Extract the DNS request ID from the binary query."""
    return str(DNSRecord.parse(dns_bytes).header.id)

def create_app():
    app = Flask(__name__)

    # Configure logging with timestamps
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
    )

    def is_rate_limited(ip: str, limit: int = 100, window: int = 60) -> tuple[bool, int]:
        """
        Sliding window rate limiter.

        Returns:
            (True, ttl) if limited
            (False, remaining) if allowed
        """
        key = f"ratelimit:{ip}"
        try:
            count = redis_client.incr(key)
            if count == 1:
                redis_client.expire(key, window)

            if count > limit:
                ttl = redis_client.ttl(key)
                return True, ttl
            return False, limit - count
        except redis.RedisError:
            # Fail open: don't block requests if Redis fails
            return False, -1

    
    @app.route("/healthz")
    def health():
        return "ok", 200


    @app.route("/dns/queries", methods=["POST"])
    def dns_query():
        ip = request.remote_addr or "unknown"
        limited, extra = is_rate_limited(ip)
        logging.info(f"Accessed /dns/queries endpoint from {ip}")

        if limited:
            response = jsonify({"error": "Rate limit exceeded. Please try again later."})
            response.status_code = 429
            if extra > 0:
                response.headers["Retry-After"] = str(extra)
            return response

        try:
            raw_data = request.get_data()
            if not raw_data:
                return jsonify({"error": "No data provided"}), 400

            base64_query = raw_data.decode("utf-8")
            decoded_bytes, questions = decode_and_parse_dns_query(base64_query)
            request_id = parse_request_id(decoded_bytes)

            # ETag validation
            client_etag = request.headers.get("If-None-Match")
            if client_etag and client_etag.strip('"') == request_id:
                logging.info(f"ETag matched: {request_id} – returning 304 Not Modified")
                return '', 304

            # Resolve DNS query
            answers, resolver_used = resolve_dns_query(decoded_bytes)

            response_data = {
                "id": request_id,
                "questions": questions,
                "answers": answers,
                "resolver": resolver_used
            }

            logging.info(f"Response: {response_data}")

            response = make_response(jsonify(response_data))
            response.headers["Cache-Control"] = "public, max-age=3600"
            response.headers["ETag"] = request_id
            return response

        except Exception as e:
            logging.error(f"Failed to process request: {e}")
            return jsonify({"error": str(e)}), 400

    return app
