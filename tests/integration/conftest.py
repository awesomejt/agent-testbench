import os
import pytest
import httpx


@pytest.fixture(scope="session")
def api_url() -> str:
    return os.environ.get("TESTBENCH_API_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def client(api_url: str):
    with httpx.Client(base_url=api_url, timeout=10) as c:
        yield c
