import uuid
from logging import getLogger
from os import getenv as os_getenv

import azure.functions as func

from image_processing_function_app.exceptions import ImageProcessingError
from image_processing_function_app.processing import ImageProcessingFunctionRequest

LOGGER = getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:

    LOGGER.info("Python HTTP trigger function processed a request.")

    # Set environment variables for Azure Storage
    azure_storage_connection_string = os_getenv("AZURE_STORAGE_CONNECTION_STRING")
    azure_storage_container_name = os_getenv("AZURE_STORAGE_CONTAINER_NAME")

    # Set environment variables for Azure Table Storage
    azure_table_connection_string = os_getenv("AZURE_TABLE_CONNECTION_STRING")
    azure_table_name = os_getenv("AZURE_TABLE_NAME")
    azure_table_partition_key = os_getenv("AZURE_TABLE_PARTITION_KEY")
    azure_table_row_key = os_getenv("AZURE_TABLE_ROW_KEY")

    # Generate a unique blob name
    blob_name = uuid.uuid4()
    blob_file_name = str(blob_name) + ".jpg"

    # Create an instance of ImageProcessingFunctionRequest
    img_proc_func_request = ImageProcessingFunctionRequest.from_http_request(
        req=req,
        logger=LOGGER,
    )

    try:
        # Upload image to blob storage
        img_proc_func_request.upload_to_blob_storage(
            connection_string=str(azure_storage_connection_string),
            container_name=str(azure_storage_container_name),
            blob_file_name=str(blob_file_name),
        )

        # Insert record into table storage
        img_proc_func_request.insert_table_storage_record(
            connection_string=str(azure_table_connection_string),
            table_name=str(azure_table_name),
            blob_file_name=str(blob_file_name),
            partition_key=str(azure_table_partition_key),
            row_key=str(azure_table_row_key),
        )

    except ImageProcessingError:
        return func.HttpResponse(
            "Error occurred while processing image",
            status_code=500,
        )

    LOGGER.info("Image processing function completed successfully.")

    return func.HttpResponse(
        "Image processing function completed successfully.",
        status_code=200,
    )
