class ImageProcessingError(Exception):
    """Base class for exceptions in the image processing function app."""

    pass


class MetadataError(Exception):
    """Exception raised for errors in the metadata."""

    pass


class BlobStorageError(Exception):
    """Exception raised for errors in the blob storage."""

    pass


class TableStorageError(Exception):
    """Exception raised for errors in the table storage."""

    pass
