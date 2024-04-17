from logging import Logger, getLogger

import azure.functions as func
from azure.data.tables import UpdateMode

from image_processing_function_app.connectors.azurestorage import (
    insert_table_storage_record,
    upload_to_blob_storage,
)
from image_processing_function_app.exceptions import (
    BlobStorageError,
    ImageProcessingError,
    MetadataError,
    TableStorageError,
)
from image_processing_function_app.metadata import (
    METADATA_DEFAULT,
    Metadata,
    get_metadata,
)

LOGGER = getLogger(__name__)


class ImageProcessingFunctionRequest:
    """Represents a request to an image processing function."""

    def __init__(
        self,
        req: func.HttpRequest,
        logger: Logger,
    ):
        """Initializes the ImageProcessingFunctionRequest.

        Args:
            req (func.HttpRequest): The HTTP request.
            logger (Logger): The logger.
        """
        self.logger = logger
        self.method = req.method
        self.url = req.url
        self.headers = req.headers
        self.params = req.params
        self.route_params = req.route_params
        self.body = req.get_body()
        self.metadata: Metadata = self.__get_metadata()

    @classmethod
    def from_http_request(
        cls,
        req: func.HttpRequest,
        logger: Logger = LOGGER,
    ) -> "ImageProcessingFunctionRequest":
        """Creates an ImageProcessingFunctionRequest from an HTTP request.

        Args:
            req (func.HttpRequest): The HTTP request.
            logger (Logger, optional): The logger. Defaults to LOGGER.

        Returns:
            ImageProcessingFunctionRequest: The ImageProcessingFunctionRequest.
        """
        return cls(req=req, logger=logger)

    @property
    def metadata_dict(self):
        """Returns the metadata as a dictionary."""
        return {
            "make": str(self.metadata.make),
            "exif_ifd_pointer": str(self.metadata.exif_ifd_pointer),
            "gps_ifd_pointer": str(self.metadata.gps_ifd_pointer),
        }

    def upload_to_blob_storage(
        self,
        connection_string: str,
        container_name: str,
        blob_file_name: str,
        **kwargs,
    ):
        """Uploads the image to blob storage.

        Args:
            connection_string (str): The connection string.
            container_name (str): The container name.
            blob_file_name (str): The blob file name.

        Raises:
            ImageProcessingError: An error occurred while uploading the image to blob storage.
        """
        try:
            upload_to_blob_storage(
                connection_string=connection_string,
                container_name=container_name,
                blob_file_name=blob_file_name,
                data=self.body,
                metadata=self.metadata_dict,
                **kwargs,
            )
        except BlobStorageError as e:
            self.logger.error(f"Failed to upload image to blob storage: {e}")
            raise ImageProcessingError("Failed to upload image to blob storage.") from e

    def insert_table_storage_record(
        self,
        connection_string: str,
        table_name: str,
        blob_file_name: str,
        partition_key: str,
        row_key: str,
        mode: UpdateMode = UpdateMode.MERGE,
        **kwargs,
    ):
        """Inserts a record to table storage.

        Args:
            connection_string (str): The connection string.
            table_name (str): The table name.
            blob_file_name (str): The blob file name.
            partition_key (str): The partition key.
            row_key (str): The row key.
            mode (UpdateMode, optional): The update mode. Defaults to UpdateMode.MERGE.

        Raises:
            ImageProcessingError: An error occurred while inserting the record to table storage.
        """
        try:
            insert_table_storage_record(
                connection_string=connection_string,
                table_name=table_name,
                entity={
                    "PartitionKey": str(partition_key),
                    "RowKey": str(row_key),
                    "BlobName": str(blob_file_name),
                    **self.metadata_dict,
                },
                mode=mode,
                **kwargs,
            )
        except TableStorageError as e:
            self.logger.error(f"Failed to insert record to table storage: {e}")
            raise ImageProcessingError(
                "Failed to insert record to table storage."
            ) from e

    def __get_metadata(self) -> Metadata:
        """Extracts metadata from the image.

        Returns:
            Metadata: The metadata extracted from the image.
        """
        try:
            return get_metadata(binary_image=self.body)
        except MetadataError as e:
            self.logger.warning(e)
            return METADATA_DEFAULT
