import base64
import pytest
from dns_querier.main import create_app
from dns_querier.config import extract_request_id

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()

def test_valid_dns_query(client):
    # DNS query for www.google.com with ID abcd (hex)
    dns_hex = 'abcd010000010000000000000377777706676f6f676c6503636f6d0000010001'
    dns_bytes = bytes.fromhex(dns_hex)
    base64_query = base64.b64encode(dns_bytes).decode('utf-8')

    response = client.post('/dns/queries', data=base64_query)
    
    assert response.status_code == 200
    json_data = response.get_json()
    
    assert json_data["id"] == "abcd"
    assert len(json_data["questions"]) == 1
    assert json_data["questions"][0]["name"] == "www.google.com."
    assert json_data["questions"][0]["type"] == "1"  # A record

def test_empty_request_body(client):
    response = client.post('/dns/queries', data="")
    assert response.status_code == 400
    assert response.get_json()["error"] == "No data provided"

def test_malformed_base64(client):
    response = client.post('/dns/queries', data="@@@invalid@@@")
    assert response.status_code == 400
    assert "Invalid DNS query format" in response.get_json()["error"]

def test_short_query_less_than_two_bytes(client):
    short_encoded = base64.b64encode(b'\x01').decode('utf-8')
    response = client.post('/dns/queries', data=short_encoded)
    assert response.status_code == 400
    assert "Invalid DNS query format" in response.get_json()["error"]

def test_extract_request_id_too_short():
    with pytest.raises(ValueError, match="DNS data too short to contain transaction ID"):
        extract_request_id(b'\x01')
