import base64
import logging
from dnslib import DNSRecord

logging.basicConfig(level=logging.INFO)

def decode_and_parse_dns_query(encoded_data: str):
    """
    Decode base64-encoded DNS query and extract questions.

    Returns:
        - raw decoded bytes
        - list of questions: [{name, type}]
    Raises:
        ValueError if the input is not a valid DNS query.
    """
    try:
        decoded_bytes = base64.b64decode(encoded_data)
        dns_record = DNSRecord.parse(decoded_bytes)

        questions = []
        for q in dns_record.questions:
            questions.append({
                "name": str(q.get_qname()),
                "type": q.qtype,  # numeric QTYPE
                "type_name": str(q.qtype)  # str(QTYPE) gives readable name like "A"
            })

        return decoded_bytes, questions
    except Exception as e:
        logging.error(f"Failed to parse DNS query: {e}")
        raise ValueError("Invalid DNS query format")
