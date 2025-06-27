import json
import logging
import sys
from flask import Flask, request, jsonify, make_response
from dns_querier.utils import decode_and_parse_dns_query
from dns_querier.config import extract_request_id

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Set up custom logging with timestamp
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def create_app():
    app = Flask(__name__)

    @app.route("/healthz", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok"}), 200

    @app.route("/dns/queries", methods=["POST"])
    def dns_query():
        logging.info("Accessed /dns/queries endpoint")

        try:
            raw_data = request.get_data()
            if not raw_data:
                return jsonify({"error": "No data provided"}), 400

            base64_query = raw_data.decode('utf-8')
            decoded_bytes, questions = decode_and_parse_dns_query(base64_query)
            req_id = extract_request_id(decoded_bytes)

            response_data = {
                "id": req_id,
                "questions": questions
            }

            # Log JSON response
            logging.info("Response JSON: %s", json.dumps(response_data))

            response = make_response(jsonify(response_data))
            response.headers["Cache-Control"] = "public, max-age=3600"
            response.headers["ETag"] = req_id

            return response
        except ValueError as ve:
            logging.error(f"Error: {ve}")
            return jsonify({"error": str(ve)}), 400

    return app
