import base64
import logging
from dnslib import DNSRecord, QTYPE

logging.basicConfig(level=logging.INFO)

def decode_and_parse_dns_query(encoded_data: str):
    try:
        decoded_bytes = base64.b64decode(encoded_data)
        dns_record = DNSRecord.parse(decoded_bytes)
        questions = [{
            "name": str(q.get_qname()),
            "type": str(QTYPE[q.qtype])
        } for q in dns_record.questions]
        return decoded_bytes, questions
    except Exception as e:
        logging.error(f"Failed to parse DNS query: {e}")
        raise ValueError("Invalid DNS query format")
