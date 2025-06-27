import base64
import time
import requests
import socket
from multiprocessing import Process
from testcontainers.redis import RedisContainer
from dns_querier.main import create_app

DNS_HEX = 'abcd010000010000000000000377777706676f6f676c6503636f6d0000010001'
DNS_BYTES = bytes.fromhex(DNS_HEX)
BASE64_QUERY = base64.b64encode(DNS_BYTES).decode("utf-8")
PORT = 5005  # Avoid conflict with local server

def run_flask_server(redis_host: str, redis_port: str):
    import os
    import logging
    os.environ["REDIS_HOST"] = redis_host
    os.environ["REDIS_PORT"] = redis_port

    logging.basicConfig(level=logging.DEBUG)
    app = create_app()
    app.run(host="0.0.0.0", port=PORT, debug=True, use_reloader=False)


def wait_for_server(timeout=10):
    print("Waiting for server to become available...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(f"http://localhost:{PORT}/healthz")
            if resp.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.5)
    raise TimeoutError("Server failed to start in time")


def test_rate_limit_exceeded():
    with RedisContainer(image="redis:7.2-alpine") as redis:
        redis_host = redis.get_container_host_ip()
        redis_port = redis.get_exposed_port(6379)

        server_proc = Process(target=run_flask_server, args=(redis_host, redis_port))
        server_proc.start()

        try:
            wait_for_server()

            url = f"http://localhost:{PORT}/dns/queries"
            headers = {"Content-Type": "text/plain"}

            success = 0
            fail = 0

            for i in range(105):
                try:
                    resp = requests.post(url, data=BASE64_QUERY, headers=headers)
                    if resp.status_code == 429:
                        fail += 1
                    elif resp.status_code == 200:
                        success += 1
                except Exception as e:
                    print(f"Request failed: {e}")

            assert success == 100
            assert fail >= 1
        finally:
            server_proc.terminate()
            server_proc.join()

