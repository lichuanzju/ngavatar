"""This module defines exceptions that may be raised in this package"""


class NGError(Exception):
    """Base class for exceptions in this package"""
    pass


class FileReadError(NGError):
    """Exception that is raised when failed to read a file"""

    def __init__(self, filepath):
        """Create file read error with path to the file."""
        self.filepath = filepath

    def __str__(self):
        """Return description of this error."""
        return 'Failed to read file "%s"' % self.filepath


class TemplateFormatError(NGError):
    """Exception that is raised when format of a template is illegal."""

    def __init__(self, template_filepath, reason=None):
        """Create template format error with path to the file."""
        self.template_filepath = template_filepath
        self.reason = reason

    def __str__(self):
        """Return description of this error."""
        return 'Template file "%s" has illegal format: %s'\
             % (self.template_filepath, self.reason)


def test_Exceptions():
    try:
        raise FileReadError('/tmp/view')
    except FileReadError as e:
        print e

    try:
        raise TemplateFormatError('/tmp/template.html')
    except TemplateFormatError as e:
        print e


if __name__ == '__main__':
    test_Exceptions()
