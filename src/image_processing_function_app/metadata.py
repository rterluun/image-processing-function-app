from dataclasses import dataclass

from exif import Image

from image_processing_function_app.exceptions import MetadataError


@dataclass
class Metadata:
    """Metadata extracted from an image."""

    make: str
    exif_ifd_pointer: str
    gps_ifd_pointer: str


METADATA_DEFAULT = Metadata(
    make="Unknown",
    exif_ifd_pointer="Unknown",
    gps_ifd_pointer="Unknown",
)


def get_metadata(binary_image: bytes) -> Metadata:
    """Extracts metadata from an image.

    Args:
        binary_image (bytes): The binary image data.

    Raises:
        MetadataError: An error occurred while extracting metadata from the image.

    Returns:
        Metadata: The metadata extracted from the image.
    """
    try:
        metadata_from_image = Image(binary_image)
        return Metadata(
            make=metadata_from_image.make,
            exif_ifd_pointer=str(metadata_from_image.get("_exif_ifd_pointer")),
            gps_ifd_pointer=str(metadata_from_image.get("_gps_ifd_pointer")),
        )
    except Exception as e:
        raise MetadataError(f"Failed to extract metadata from image: {e}") from e
