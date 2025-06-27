import pytest
from testcontainers.redis import RedisContainer
from dns_querier.resolver import resolve_dns_query
from dns_querier.main import create_app

@pytest.fixture(scope="module", autouse=True)
def flask_with_redis():
    with RedisContainer(image="redis:7.2-alpine") as redis:
        import os
        os.environ["REDIS_HOST"] = redis.get_container_host_ip()
        os.environ["REDIS_PORT"] = redis.get_exposed_port(6379)
        yield create_app().test_client()

def test_dns_resolution(flask_with_redis):
    dns_hex = "abcd010000010000000000000377777706676f6f676c6503636f6d0000010001"
    dns_bytes = bytes.fromhex(dns_hex)
    answers, resolver = resolve_dns_query(dns_bytes)

    assert isinstance(answers, list)
    assert len(answers) > 0
    assert "rdata" in answers[0]
