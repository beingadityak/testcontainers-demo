import base64
import pytest
from testcontainers.redis import RedisContainer
from dns_querier.utils import decode_and_parse_dns_query
from dns_querier.main import create_app

@pytest.fixture(scope="module", autouse=True)
def flask_with_redis():
    with RedisContainer(image="redis:7.2-alpine") as redis:
        import os
        os.environ["REDIS_HOST"] = redis.get_container_host_ip()
        os.environ["REDIS_PORT"] = redis.get_exposed_port(6379)
        yield create_app().test_client()

def test_valid_dns_query(flask_with_redis):
    dns_hex = 'abcd010000010000000000000377777706676f6f676c6503636f6d0000010001'
    dns_bytes = bytes.fromhex(dns_hex)
    base64_encoded = base64.b64encode(dns_bytes).decode('utf-8')

    decoded, questions = decode_and_parse_dns_query(base64_encoded)
    assert decoded == dns_bytes
    assert questions[0]["name"] == "www.google.com."
    assert questions[0]["type_name"] == "1"

def test_invalid_base64(flask_with_redis):
    with pytest.raises(ValueError):
        decode_and_parse_dns_query("!!not-base64@@")
