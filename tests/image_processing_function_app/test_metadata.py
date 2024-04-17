import pytest

from image_processing_function_app.exceptions import MetadataError
from image_processing_function_app.metadata import Metadata, get_metadata


def test_get_metadata(test_image: bytes):
    """Test get_metadata function."""
    assert get_metadata(binary_image=test_image) == Metadata(
        make="Python",
        exif_ifd_pointer=57,
        gps_ifd_pointer=63,
    )


def test_get_metadata_empty_image():
    """Test get_metadata function with empty image."""
    with pytest.raises(
        MetadataError, match="Failed to extract metadata from image: 'APP1'"
    ):
        get_metadata(binary_image=b"")
