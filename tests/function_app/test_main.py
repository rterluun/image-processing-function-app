from unittest.mock import MagicMock, patch
from uuid import UUID

import azure.functions as func
from azure.data.tables import TableServiceClient, UpdateMode
from azure.storage.blob import BlobServiceClient

from image_processing_function_app.exceptions import ImageProcessingError
from v1 import main


@patch.object(TableServiceClient, "from_connection_string", return_value=MagicMock())
@patch.object(BlobServiceClient, "from_connection_string", return_value=MagicMock())
@patch("uuid.uuid4", return_value=UUID(int=1))
def test_main(
    mock_uuid4: MagicMock,
    mock_blob_service_client: MagicMock,
    mock_table_service_client: MagicMock,
    test_request: func.HttpRequest,
    test_image: bytes,
):
    """Test main function."""
    blob_file_name = str(mock_uuid4.return_value) + ".jpg"
    http_response = main(req=test_request)

    # Test HTTP response status code is 200
    assert http_response.status_code == 200

    # Test HTTP response body is correct
    assert http_response.get_body() == b"Image processing function completed successfully."

    # Test container name is set correctly from environment variable
    mock_blob_service_client.return_value.get_blob_client.assert_called_once_with(
        container="azure_storage_container_name",
        blob=blob_file_name,
    )

    # Test blob is uploaded with correct metadata
    mock_blob_service_client.return_value.get_blob_client.return_value.upload_blob.assert_called_once_with(
        data=test_image,
        blob_type="BlockBlob",
        metadata={
            "make": "Python",
            "exif_ifd_pointer": "57",
            "gps_ifd_pointer": "63",
        },
    )

    # Test table name is set correctly from environment variable
    mock_table_service_client.return_value.get_table_client.assert_called_once_with(table_name="table_name")

    # Test entity is inserted into table storage with correct metadata
    mock_table_service_client.return_value.get_table_client.return_value.upsert_entity.assert_called_once_with(
        entity={
            "PartitionKey": "PK",
            "RowKey": "RK",
            "BlobName": blob_file_name,
            "make": "Python",
            "exif_ifd_pointer": "57",
            "gps_ifd_pointer": "63",
        },
        mode=UpdateMode.MERGE,
    )


@patch.object(TableServiceClient, "from_connection_string", return_value=MagicMock())
@patch.object(BlobServiceClient, "from_connection_string", return_value=MagicMock())
@patch("image_processing_function_app.processing.upload_to_blob_storage")
def test_main_storage_error(
    mock_upload_to_blob_storage: MagicMock,
    mock_blob_service_client: MagicMock,
    mock_table_service_client: MagicMock,
    test_request: func.HttpRequest,
):
    """Test main function with blob storage error."""
    mock_upload_to_blob_storage.side_effect = ImageProcessingError("An error occurred")
    http_response = main(req=test_request)

    # Test HTTP response status code is 500
    assert http_response.status_code == 500

    # Test HTTP response body is correct
    assert http_response.get_body() == b"Error occurred while processing image"

    # Test that both upload_to_blob_storage and insert_table_storage_record are not called
    mock_blob_service_client.return_value.get_blob_client.assert_not_called()
    mock_table_service_client.return_value.get_table_client.assert_not_called()


@patch.object(TableServiceClient, "from_connection_string", return_value=MagicMock())
@patch.object(BlobServiceClient, "from_connection_string", return_value=MagicMock())
@patch("image_processing_function_app.processing.insert_table_storage_record")
def test_main_table_error(
    mock_insert_table_storage_record: MagicMock,
    mock_blob_service_client: MagicMock,
    mock_table_service_client: MagicMock,
    test_request: func.HttpRequest,
):
    """Test main function with table storage error."""
    mock_insert_table_storage_record.side_effect = ImageProcessingError("An error occurred")
    http_response = main(req=test_request)

    # Test HTTP response status code is 500
    assert http_response.status_code == 500

    # Test HTTP response body is correct
    assert http_response.get_body() == b"Error occurred while processing image"

    # Test that upload to blob storage happen when table storage error occurs
    mock_blob_service_client.return_value.get_blob_client.return_value.upload_blob.assert_called_once()
    mock_table_service_client.return_value.get_table_client.assert_not_called()
