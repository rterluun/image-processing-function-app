from unittest.mock import MagicMock, patch

import azure.functions as func
import pytest
from azure.data.tables import TableServiceClient, UpdateMode
from azure.storage.blob import BlobServiceClient

from image_processing_function_app.exceptions import ImageProcessingError
from image_processing_function_app.metadata import Metadata
from image_processing_function_app.processing import ImageProcessingFunctionRequest


def test_from_http_request(test_request: func.HttpRequest):
    """Test from_http_request method."""
    assert ImageProcessingFunctionRequest.from_http_request(
        req=test_request
    ).metadata == Metadata(
        make="Python",
        exif_ifd_pointer="57",
        gps_ifd_pointer="63",
    )


def test_from_empty_http_request(empty_request: func.HttpRequest):
    """Test from_http_request method with empty request."""
    assert ImageProcessingFunctionRequest.from_http_request(
        req=empty_request
    ).metadata == Metadata(
        make="Unknown",
        exif_ifd_pointer="Unknown",
        gps_ifd_pointer="Unknown",
    )


@patch.object(BlobServiceClient, "from_connection_string", return_value=MagicMock())
def test_upload_to_blob_storage(
    mock_blob_service_client: MagicMock,
    test_request: func.HttpRequest,
    test_image: bytes,
):
    """Test upload_to_blob_storage method."""
    blob_service_client = mock_blob_service_client.return_value
    blob_client = mock_blob_service_client.return_value.get_blob_client.return_value

    ImageProcessingFunctionRequest.from_http_request(
        req=test_request
    ).upload_to_blob_storage(
        connection_string="connection_string",
        container_name="container_name",
        blob_file_name="blob_file_name",
    )

    blob_service_client.get_blob_client.assert_called_once_with(
        container="container_name",
        blob="blob_file_name",
    )

    blob_client.upload_blob.assert_called_once_with(
        data=test_image,
        blob_type="BlockBlob",
        metadata={
            "make": "Python",
            "exif_ifd_pointer": "57",
            "gps_ifd_pointer": "63",
        },
    )


@patch.object(BlobServiceClient, "from_connection_string", return_value=MagicMock())
def test_upload_to_blob_storage_error(
    mock_blob_service_client: MagicMock,
    test_request: func.HttpRequest,
):
    """Test upload_to_blob_storage method with error."""
    blob_client = mock_blob_service_client.return_value.get_blob_client.return_value
    blob_client.upload_blob.side_effect = Exception("Something went wrong")

    with pytest.raises(
        ImageProcessingError,
        match="Failed to upload image to blob storage.",
    ):
        ImageProcessingFunctionRequest.from_http_request(
            req=test_request
        ).upload_to_blob_storage(
            connection_string="connection_string",
            container_name="container_name",
            blob_file_name="blob_file_name",
        )


@patch.object(TableServiceClient, "from_connection_string", return_value=MagicMock())
def test_insert_table_storage_record(
    mock_table_service_client: MagicMock,
    test_request: func.HttpRequest,
):
    """Test insert_table_storage_record method."""
    table_service_client = mock_table_service_client.return_value
    table_client = mock_table_service_client.return_value.get_table_client.return_value

    ImageProcessingFunctionRequest.from_http_request(
        req=test_request
    ).insert_table_storage_record(
        connection_string="connection_string",
        table_name="table_name",
        blob_file_name="blob_file_name",
        partition_key="PK",
        row_key="RK",
    )

    table_service_client.get_table_client.assert_called_once_with(
        table_name="table_name"
    )
    table_client.upsert_entity.assert_called_once_with(
        entity={
            "PartitionKey": "PK",
            "RowKey": "RK",
            "BlobName": "blob_file_name",
            "make": "Python",
            "exif_ifd_pointer": "57",
            "gps_ifd_pointer": "63",
        },
        mode=UpdateMode.MERGE,
    )


@patch.object(TableServiceClient, "from_connection_string", return_value=MagicMock())
def test_insert_table_storage_record_error(
    mock_table_service_client: MagicMock,
    test_request: func.HttpRequest,
):
    """Test insert_table_storage_record method with error."""
    table_client = mock_table_service_client.return_value.get_table_client.return_value
    table_client.upsert_entity.side_effect = Exception("Something went wrong")

    with pytest.raises(
        ImageProcessingError,
        match="Failed to insert record to table storage.",
    ):
        ImageProcessingFunctionRequest.from_http_request(
            req=test_request
        ).insert_table_storage_record(
            connection_string="connection_string",
            table_name="table_name",
            blob_file_name="blob_file_name",
            partition_key="PK",
            row_key="RK",
        )
