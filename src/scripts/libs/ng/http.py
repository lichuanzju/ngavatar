"""This module defines classes directly related HTTP request processing."""


import abc
import datetime
import sys
import str_generator
from database import MySQLDatabase
from models import Session


def status_description(status_code):
    """Return description of a specified http status code."""
    # Use attribute of function to avoid duplicated creation
    if not hasattr(status_description, '_http_status_description'):
        status_description._http_status_description = {
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

    return status_description._http_status_description.\
        get(status_code, 'Unknow Status')


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
        self.script_name = environ.get('SCRIPT_NAME', '')
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

    def add_header(self, name, value):
        """Add extra header to this response."""
        self.headers[name] = value

    def set_cookie(self, cookie):
        """Add cookie to this response."""
        if cookie is not None:
            self.headers['Set-Cookie'] = cookie.http_header()

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
        # Check the output file
        if out is None:
            out = sys.stdout

        # Generate header string and body
        header_string = self._get_header_string()
        if self.view is None:
            body = ''
        else:
            body = self.view.render_body()

        # Write everything to output
        out.write(header_string)
        out.write('\r\n\r\n')
        out.write(body)
        out.flush()


class HttpRedirectResponse(HttpResponse):
    """The HTTP response that redirects the request."""

    def __init__(self, redirect_location):
        """Create redirect response with the redirecting location."""
        HttpResponse.__init__(self, None)
        self.headers['Status'] = status_header(302)
        self.headers['Location'] = redirect_location


class HttpErrorResponse(HttpResponse):
    """The HTTP response that indicates an HTTP error."""

    def __init__(self, error_code, error_view):
        """Create error response with error code and path to error page."""
        HttpResponse.__init__(self,
                              error_view,
                              Status=status_header(error_code))


class HttpSession(object):
    """Abstract class that defines API of http session."""

    __metaclass__ = abc.ABCMeta

    @classmethod
    @abc.abstractmethod
    def create_session(cls, storage, data, client_ip, effective_hours):
        """Create a new session. client_ip specifies the IP address of the
        HTTP client. effective_hours specifies effective time in hours.
        data collects the data to store in the session."""
        pass

    @classmethod
    @abc.abstractmethod
    def load_session(cls, storage, session_key):
        """Load the session with specified session key."""
        pass

    @abc.abstractmethod
    def get_session_key(self):
        """Return the key of this session."""
        pass

    @abc.abstractmethod
    def get_attribute(self, attribute_name, default=None):
        """Get attribute stored in this session with specified name."""
        pass

    @abc.abstractmethod
    def set_attribute(self, attribute_name, attribute_value):
        """Set the value of attribute with specified name."""
        pass

    @abc.abstractmethod
    def expired(self):
        """Return whether this session has expired."""
        pass

    @abc.abstractmethod
    def renew(self, effective_hours):
        """Renew the expiring time of this session."""
        pass

    @abc.abstractmethod
    def get_expire_time(self):
        """Get the expire time of this session."""
        pass

    @abc.abstractmethod
    def invalidate(self):
        """Remove this session."""
        pass


class DatabaseSession(HttpSession):
    """Http session implemented with database."""

    def __init__(self, db, model):
        """Create session object."""
        self.db = db
        self.model = model

    @classmethod
    def create_session(cls, db, data, client_ip, effective_hours):
        """Create a new session in database and return it. None is returned
        if failed."""
        # Try 3 times
        for trial in range(3):
            session_key = str_generator.unique_id(40)

            session_model = Session.create_session(
                db,
                session_key,
                data,
                client_ip,
                effective_hours
            )

            if session_model is not None:
                break

        # If still not created, return None
        if session_model is None:
            return None
        else:
            return DatabaseSession(db, session_model)

    @classmethod
    def load_session(cls, db, session_key):
        """Load session from database with session_key."""
        session_model = Session.load_from_database(db,
                                                   session_key=session_key)

        if session_model is None:
            return None
        else:
            return DatabaseSession(db, session_model)

    def get_session_key(self):
        """Return the key of this session."""
        return self.model['session_key']

    def get_attribute(self, attribute_name, default=None):
        """Get attribute stored in this session with specified name."""
        return self.model.get_data_attribute(attribute_name, default)

    def set_attribute(self, attribute_name, attribute_value):
        """Set the value of attribute with specified name."""
        self.model.set_data_attribute(attribute_name,
                                      attribute_value)
        self.model.store_session_data(self.db)

    def get_expire_time(self):
        """Get the expire time of this session."""
        return self.model['expire_time']

    def expired(self):
        """Return whether this session has expired."""
        return self.model.session_expired()

    def renew(self, effective_hours):
        """Renew the expiring time of this session."""
        return self.model.renew_session(self.db, effective_hours)

    def invalidate(self):
        """Remove this session."""
        self.model.delete_from_database(self.db)
