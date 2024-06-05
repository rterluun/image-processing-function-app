from dataclasses import dataclass

import azure.functions as func
from werkzeug.datastructures import ImmutableMultiDict

from image_processing_function_app.exceptions import MultiPartDataError


@dataclass
class MultiPartData:
    """Represents multipart data."""

    metadata: bytes
    image: bytes


MULTIPARTDATA_DEFAULT = MultiPartData(
    metadata=b"Unknown",
    image=b"Unknown",
)


def get_multiparts(req: func.HttpRequest) -> MultiPartData:
    """Extracts multipart data from an HTTP request.

    Args:
        req (func.HttpRequest): The HTTP request.

    Raises:
        MultiPartDataError: An error occurred while extracting multipart data from the request.

    Returns:
        MultiPartData: The multipart data extracted from the request.
    """
    try:
        multi_dict: ImmutableMultiDict = req.files

        return MultiPartData(
            metadata=multi_dict.get("metadata").stream.read(),
            image=multi_dict.get("file").stream.read(),
        )
    except Exception as e:
        raise MultiPartDataError(f"Failed to extract multipart data: {e}") from e
