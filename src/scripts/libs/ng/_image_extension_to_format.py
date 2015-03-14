"""This module defines the utility functions for converting image
extension to format."""


def image_format_from_extension(extension):
    """Get image format from its extension."""
    if not hasattr(image_format_from_extension, '_image_formats'):
        image_format_from_extension._image_formats = {
            '.bmp': 'bmp',
            '.fax': 'fax',
            '.gif': 'gif',
            '.ico': 'x-icon',
            '.jpe': 'jpeg',
            '.jpeg': 'jpeg',
            '.tif': 'tiff',
            '.tiff': 'tiff',
            '.png': 'png',
        }

    return image_format_from_extension._image_formats.\
        get(extension, 'jpeg')
