from unittest.mock import MagicMock, patch

import pytest
from azure.data.tables import TableServiceClient, UpdateMode
from azure.storage.blob import BlobServiceClient

from image_processing_function_app.connectors.azurestorage import (
    insert_table_storage_record, upload_to_blob_storage)
from image_processing_function_app.exceptions import (BlobStorageError,
                                                      TableStorageError)


@patch.object(BlobServiceClient, "from_connection_string", return_value=MagicMock())
def test_upload_to_blob_storage(mock_blob_service_client: MagicMock):
    """Test upload_to_blob_storage function."""
    blob_service_client = mock_blob_service_client.return_value
    blob_client = mock_blob_service_client.return_value.get_blob_client.return_value

    upload_to_blob_storage(
        connection_string="connection_string",
        container_name="container_name",
        blob_file_name="blob_file_name",
        data=b"example",
        metadata={"tag": "tag_example"},
    )

    blob_service_client.get_blob_client.assert_called_once_with(
        container="container_name",
        blob="blob_file_name",
    )

    blob_client.upload_blob.assert_called_once_with(
        data=b"example", blob_type="BlockBlob", metadata={"tag": "tag_example"}
    )


@patch.object(BlobServiceClient, "from_connection_string", return_value=MagicMock())
def test_upload_to_blob_storage_error(mock_blob_service_client: MagicMock):
    """Test upload_to_blob_storage function with error."""
    blob_client = mock_blob_service_client.return_value.get_blob_client.return_value
    blob_client.upload_blob.side_effect = Exception("Something went wrong")

    with pytest.raises(
        BlobStorageError,
        match="Something went wrong",
    ):
        upload_to_blob_storage(
            connection_string="connection_string",
            container_name="container_name",
            blob_file_name="blob_file_name",
            data=b"example",
        )


@patch.object(TableServiceClient, "from_connection_string", return_value=MagicMock())
def test_insert_table_storage_record(mock_table_service_client: MagicMock):
    """Test insert_table_storage_record function."""
    table_service_client = mock_table_service_client.return_value
    table_client = mock_table_service_client.return_value.get_table_client.return_value

    insert_table_storage_record(
        connection_string="connection_string",
        table_name="table_name",
        entity={"PartitionKey": "PK", "RowKey": "RK"},
        mode=UpdateMode.MERGE,
    )

    table_service_client.get_table_client.assert_called_once_with(
        table_name="table_name"
    )

    table_client.upsert_entity.assert_called_once_with(
        entity={"PartitionKey": "PK", "RowKey": "RK"},
        mode=UpdateMode.MERGE,
    )


@patch.object(TableServiceClient, "from_connection_string", return_value=MagicMock())
def test_insert_table_storage_error(mock_table_service_client: MagicMock):
    """Test insert_table_storage_record function with error."""
    table_client = mock_table_service_client.return_value.get_table_client.return_value
    table_client.upsert_entity.side_effect = Exception("Something went wrong")

    with pytest.raises(
        TableStorageError,
        match="Something went wrong",
    ):
        insert_table_storage_record(
            connection_string="connection_string",
            table_name="table_name",
            entity={"PartitionKey": "PK", "RowKey": "RK"},
            mode=UpdateMode.MERGE,
        )
