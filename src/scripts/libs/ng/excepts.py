"""This module defines exceptions that may be raised in this package."""


class NGError(StandardError):
    """Base class for exceptions in this package."""
    pass


class HttpError(NGError):
    """Error that is raised when an HTTP error code is required to send."""

    def __init__(self, error_code, **extra_headers):
        "Create an HTTP error with HTTP error code."
        self.error_code = error_code
        self.extra_headers = extra_headers

    def __str__(self):
        "Return description of this error."
        return 'HTTP error with code %d' % self.error_code


class FileLocateError(HttpError):
    """Error that is raised when failed to locate a file."""

    def __init__(self, filepath):
        """Create file locate error with path to the file."""
        HttpError.__init__(self, 404)
        self.filepath = filepath

    def __str__(self):
        """Return description of this error."""
        return 'Failed to locate file "%s"' % self.filepath


class FileReadError(HttpError):
    """Error that is raised when failed to read a file."""

    def __init__(self, filepath):
        """Create file read error with path to the file."""
        HttpError.__init__(self, 403)
        self.filepath = filepath

    def __str__(self):
        """Return description of this error."""
        return 'Failed to read file "%s"' % self.filepath


class FileWriteError(HttpError):
    """Error that is raised when failed to write a file."""

    def __init__(self, filepath):
        """Create file write error with path to the file."""
        HttpError.__init__(self, 500)
        self.filepath = filepath

    def __str__(self):
        """Return description of this error."""
        return 'Failed to write file "%s"' % self.filepath
