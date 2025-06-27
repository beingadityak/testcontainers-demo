# -*- coding: utf-8 -*-

def extract_request_id(data: bytes) -> str:
    if len(data) < 2:
        raise ValueError("DNS data too short to contain transaction ID")
    return data[:2].hex()