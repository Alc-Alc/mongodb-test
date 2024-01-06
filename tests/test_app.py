from collections.abc import Iterator

from litestar import Litestar
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
from litestar.testing import TestClient
from mongodb_test.app import app
import pytest


@pytest.fixture
def client() -> Iterator[TestClient[Litestar]]:
    with TestClient(app) as client:
        yield client


def test_show_item(client: TestClient[Litestar]):
    bar_data = {"name": "John Doe", "email": "johndoe@example.com"}
    create_response = client.post("", json=bar_data)
    assert create_response.status_code == HTTP_201_CREATED

    created_item_id = create_response.json().get("id")
    assert created_item_id is not None

    response = client.get(f"/{created_item_id}")
    assert response.status_code == HTTP_200_OK
