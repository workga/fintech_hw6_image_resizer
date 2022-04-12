import pytest
from fastapi.testclient import TestClient

from app.app import create_app


@pytest.fixture(name='app')
def fixture_app():
    return create_app()


@pytest.fixture(name='client')
def fixture_client(app):
    return TestClient(app)
