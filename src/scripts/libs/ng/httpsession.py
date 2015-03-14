"""This module defines HTTP session related classes and functions."""


import abc
import datetime
from database import MySQLDatabase
from models import Session
import str_generator


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


class DatabaseSession(HttpSession):
    """Http session implemented with database."""

    def __init__(self, db, model):
        """Create session object."""
        self.db = db
        self.model = model

    @classmethod
    def create_session(cls, db, data, client_ip, effective_hours):
        """Create a new session in database."""
        session_key = str_generator.unique_id(40)

        session_model = Session.create_session(
            db,
            session_key,
            data,
            client_ip,
            effective_hours
        )

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

    def expired(self):
        """Return whether this session has expired."""
        return self.model.session_expired()

    def renew(self, effective_hours):
        """Renew the expiring time of this session."""
        return self.model.renew_session(self.db, effective_hours)

    def invalidate(self):
        """Remove this session."""
        self.model.delete_from_database(self.db)
