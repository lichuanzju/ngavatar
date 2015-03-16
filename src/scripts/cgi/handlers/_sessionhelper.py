"""This module defines functions that help check the http session of
requests."""


import datetime
from ng.http import DatabaseSession, HttpCookie


def get_session(request, db):
    """Extract valid session from request and return the session object.
    None is returned if no valid session exists."""
    if request.cookie is None:
        return None

    session_key = request.cookie.data.get('SessionKey')

    if not session_key:
        return None

    session = DatabaseSession.load_session(db, session_key)
    if session is None:
        return None

    return session


def _expired_time():
    """Return a datetime object that is smaller than now."""
    return datetime.datetime.now() - datetime.timedelta(1)


def expire_cookie_for_session(session, path, server_name):
    """Generate http cookie that expires the specified session."""
    if session is None:
        return None

    cookie_data = dict(SessionKey=session.get_session_key())
    return HttpCookie(
        cookie_data,
        path,
        _expired_time(),
        server_name
    )
