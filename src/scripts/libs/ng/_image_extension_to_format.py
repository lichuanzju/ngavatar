"""This module defines the utility functions for converting image
extension to format"""

_image_formats = {
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

def image_format_from_extension(extension):
    """Get image format from its extension"""
    if extension in _image_formats:
        return _image_formats[extension]
    else:
        return 'jpeg'
