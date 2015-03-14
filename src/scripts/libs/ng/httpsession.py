"""This module defines HTTP session related classes and functions."""


import abc
from database import MySQLDatabase


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
    def invalidate(self):
        """Remove this session."""
        pass
