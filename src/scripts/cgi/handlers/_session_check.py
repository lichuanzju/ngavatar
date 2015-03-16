"""This module defines functions that help check the http session of
requests."""


from ng.http import DatabaseSession


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
