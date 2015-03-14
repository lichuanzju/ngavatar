"""This module defines exceptions that may be raised in this package."""


import http


class NGError(Exception):
    """Base class for exceptions in this package."""
    pass


class HttpError(NGError):
    """Error that is raised when an http error code is required to send."""

    def __init__(self, error_code):
        "Create an http error with http error code."
        self.error_code = error_code

    def http_status(self):
        """Return http status description of this error"""
        return http.status_header(self.error_code)

    def __str__(self):
        "Return description of this error."
        return http.status_description(self.error_code)


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


def test_Exceptions():
    try:
        raise FileLocateError('/tmp/view')
    except FileLocateError as e:
        print e
        print e.http_status()

    try:
        raise FileReadError('/tmp/template.html')
    except FileReadError as e:
        print e
        print e.http_status()

    try:
        raise FileWriteError('/tmp/template.html')
    except FileWriteError as e:
        print e
        print e.http_status()


if __name__ == '__main__':
    test_Exceptions()
