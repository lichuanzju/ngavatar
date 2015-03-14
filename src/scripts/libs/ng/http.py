"""This module defines classes directly related HTTP request processing."""


import sys
import datetime


# Status codes and their description
_http_status_description = {
    200: 'OK',
    301: 'Moved Permanently',
    302: 'Found',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    500: 'Internal Server Error',
    501: 'Not Implemented',
}


def status_description(status_code):
    """Return description of a specified http status code."""
    return _http_status_description.get(status_code, 'Unknow Status')


def status_header(status_code):
    """Return the status header of the code."""
    return '%d %s' % (status_code, status_description(status_code))


class HttpCookie(object):
    """Class that represent HTTP cookies."""

    @classmethod
    def parse_http_header(cls, header_string):
        """Parse the 'Cookie' value in HTTP header and create an
        HttpCookie object."""
        if not header_string:
            return None

        # Get parts seperated by ';'
        parts = [s.strip() for s in header_string.split(';')]

        # Get key-value pairs from parts
        data = {}
        for part in parts:
            if '=' in part:
                key, value = part.split('=')
                # Ignore reserved keys
                if key.lower() not in ['path', 'domain', 'expires']:
                    data[key] = value

        # Cookie send by client only contains data fields
        return cls(data, None, None)

    def __init__(self, data, path, expires,
                 domain=None, secure=False, httponly=False):
        """Create a cookie with its attributes. data is a dictionary that
        contains the data fields."""
        self.data = data
        self.path = path
        self.domain = domain
        self.expires = expires
        self.secure = secure
        self.httponly = httponly

    def http_header(self):
        """Convert this cookie to a http 'Set-Cookie' header.'"""
        if self.data is None:
            return ''

        # Get data fields
        parts = ['%s=%s' % (k, v) for k, v in self.data.items()]

        fields = {}
        # Add path
        if self.path is not None:
            fields['Path'] = self.path

        # Add expires
        if self.expires is not None:
            expires_gmt = self.expires - datetime.timedelta(hours=8)
            fields['Expires'] = \
                expires_gmt.strftime('%a, %d %b %Y %H:%M:%S GMT')

        # Add domain
        if self.domain is not None:
            fields['Domain'] = self.domain

        # Create parts(in 'key=value' or 'key')
        parts.extend(['%s=%s' % (k, v) for k, v in fields.items()])

        # Add secure flag
        if self.secure:
            parts.append('Secure')

        # Add http only flag
        if self.httponly:
            parts.append('HttpOnly')

        return '; '.join(parts)

    def __str__(self):
        """Return description of this cookie."""
        return self.http_header()


class HttpRequest(object):
    """HTTP request class that stores information of the client request."""

    def __init__(self, environ, field_storage):
        """Create request object with environment variables and cgi
        FieldStorage object."""
        # Get request parameters
        self.method = environ.get('REQUEST_METHOD')
        self.uri = environ.get('REQUEST_URI')
        self.client_addr = environ.get('REMOTE_ADDR')
        self.useragent = environ.get('HTTP_USER_AGENT')
        self.connection = environ.get('HTTP_CONNECTION')
        self.host = environ.get('HTTP_HOST')

        # Get content attributes
        self.content_type = environ.get('CONTENT_TYPE', None)
        self.content_length = int(environ.get('CONTENT_LENGTH', '0'))

        # Get client configuration
        self.accept_format = environ.get('HTTP_ACCEPT')
        self.accept_language = environ.get('HTTP_ACCEPT_LANGUAGE')
        self.accept_encoding = environ.get('HTTP_ACCEPT_ENCODING')
        self.cache_control = environ.get('HTTP_CACHE_CONTROL')

        # Get server informathon
        self.server_name = environ.get('SERVER_NAME')
        self.server_port = environ.get('SERVER_PORT')

        # Get cookie
        self.cookie = \
            HttpCookie.parse_http_header(environ.get('HTTP_COOKIE'))

        # Get field storage passed by cgi
        self.field_storage = field_storage


class HttpResponse(object):
    """HTTP response class that stores information of server response."""

    def __init__(self, view, **headers):
        """Create HTTP response with its view."""
        self.view = view
        self.headers = headers

        if 'Content-Type' not in self.headers:
            if self.view is not None:
                self.headers['Content-Type'] = self.view.content_type
            else:
                self.headers['Content-Type'] = 'text/html'

    def add_headers(self, headers):
        """Add extra headers to this response."""
        self.headers.update(headers)

    def remove_header(self, header_name):
        """Remove the specified header from this response."""
        if header_name in self.headers:
            del self.headers[header_name]

    def _get_header_string(self):
        """Return the http header of this response."""
        # Construct header string
        header_list = []
        for key, value in self.headers.items():
            header_list.append('%s: %s' % (key, value))

        return '\r\n'.join(header_list)

    def write_to_output(self, out=None):
        """Write this response to out. If out is None or not presented,
        stdout will be used instead."""
        if out is None:
            out = sys.stdout

        out.write(self._get_header_string())
        out.write('\r\n\r\n')
        out.flush()

        if self.view is not None:
            self.view.write_to_output(out)
