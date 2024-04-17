from os import environ as os_environ

import azure.functions as func
import pytest

# The test image is a JPEG image with EXIF metadata, stored as a byte array.
with open("tests/resources/car.jpg", "rb") as f:
    TEST_IMAGE = f.read()


@pytest.fixture
def test_image():
    """Test image."""
    return TEST_IMAGE


@pytest.fixture
def test_request():
    """Test request."""
    return func.HttpRequest(
        method="POST",
        url="http://localhost/api/v1",
        headers={},
        params={},
        route_params={},
        body=TEST_IMAGE,
    )


@pytest.fixture
def empty_request():
    """Empty request."""
    return func.HttpRequest(
        method="POST",
        url="http://localhost/api/v1",
        headers={},
        params={},
        route_params={},
        body=b"",
    )


@pytest.fixture(autouse=True)
def set_env_vars():
    """Set environment variables."""
    os_environ["AZURE_STORAGE_CONNECTION_STRING"] = "azure_storage_connection_string"
    os_environ["AZURE_STORAGE_CONTAINER_NAME"] = "azure_storage_container_name"
    os_environ["AZURE_TABLE_CONNECTION_STRING"] = "table_connection_string"
    os_environ["AZURE_TABLE_NAME"] = "table_name"
    os_environ["AZURE_TABLE_PARTITION_KEY"] = "PK"

    yield

    os_environ.pop("AZURE_STORAGE_CONNECTION_STRING", None)
    os_environ.pop("AZURE_STORAGE_CONTAINER_NAME", None)
    os_environ.pop("AZURE_TABLE_CONNECTION_STRING", None)
    os_environ.pop("AZURE_TABLE_NAME", None)
    os_environ.pop("AZURE_TABLE_PARTITION_KEY", None)
