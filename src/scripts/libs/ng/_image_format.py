"""This module defines the utility functions for converting image
extension to format."""


def format_from_extension(extension):
    """Get image format from its extension."""
    if not hasattr(format_from_extension, '_image_formats'):
        format_from_extension._image_formats = {
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

    return format_from_extension._image_formats.get(extension, 'jpeg')
