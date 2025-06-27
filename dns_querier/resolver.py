import socket
import logging
from dnslib import DNSRecord

DEFAULT_EXTERNAL_RESOLVERS = ["8.8.8.8", "1.1.1.1"]

def send_dns_query(query_bytes, resolver, timeout=2):
    """
    Send raw DNS query to the specified resolver via UDP.

    Returns:
        - response_bytes
    Raises:
        socket.timeout or socket.error
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(query_bytes, (resolver, 53))
        response_bytes, _ = sock.recvfrom(512)
        return response_bytes
    finally:
        sock.close()

def resolve_dns_query(query_bytes):
    """
    Attempt to resolve using local resolver first, fallback to external resolvers.

    Returns:
        - list of answer records: [{name, type, rdata, ttl}]
        - resolver used
    Raises:
        Exception if all resolvers fail
    """
    resolvers = DEFAULT_EXTERNAL_RESOLVERS

    for resolver in resolvers:
        try:
            response_bytes = send_dns_query(query_bytes, resolver)
            dns_response = DNSRecord.parse(response_bytes)

            answers = []
            for rr in dns_response.rr:
                answers.append({
                    "name": str(rr.rname),
                    "type": rr.rtype,
                    "type_name": str(rr.rtype),
                    "rdata": str(rr.rdata),
                    "ttl": rr.ttl
                })

            return answers, resolver
        except Exception as e:
            logging.warning(f"Failed to resolve using {resolver}: {e}")
            continue

    raise Exception("Failed to resolve DNS query using all resolvers")
