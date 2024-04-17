from typing import Any, Optional

from azure.data.tables import TableServiceClient, UpdateMode
from azure.storage.blob import BlobServiceClient

from image_processing_function_app.exceptions import BlobStorageError, TableStorageError


def upload_to_blob_storage(
    connection_string: str,
    container_name: str,
    blob_file_name: str,
    data: bytes,
    metadata: Optional[dict[Any, Any]] = None,
    **kwargs: Any,
):
    """Uploads data to Azure Blob Storage.

    Args:
        connection_string (str): The connection string for the Azure Storage account.
        container_name (str): The name of the container.
        blob_file_name (str): The name of the blob.
        data (bytes): The data to upload.
        metadata (dict, optional): The metadata to associate with the blob. Defaults to None.

    Raises:
        BlobStorageError: An error occurred while uploading the data to Azure Blob Storage.
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            conn_str=connection_string
        )
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=blob_file_name
        )
        blob_client.upload_blob(
            data=data, blob_type="BlockBlob", metadata=metadata, **kwargs
        )
    except Exception as e:
        raise BlobStorageError(e) from e


def insert_table_storage_record(
    connection_string: str,
    table_name: str,
    entity: dict,
    mode: UpdateMode,
    **kwargs: Any,
):
    """Inserts a record into an Azure Table Storage table.

    Args:
        connection_string (str): The connection string for the Azure Storage account.
        table_name (str): The name of the table.
        entity (dict): The entity to insert into the table.
        mode (UpdateMode): The update mode to use when inserting the entity.

    Raises:
        TableStorageError: An error occurred while inserting the record into Azure Table Storage.
    """
    try:
        table_service_client = TableServiceClient.from_connection_string(
            conn_str=connection_string
        )
        table_client = table_service_client.get_table_client(table_name=table_name)
        table_client.upsert_entity(entity=entity, mode=mode, **kwargs)
    except Exception as e:
        raise TableStorageError(e) from e
