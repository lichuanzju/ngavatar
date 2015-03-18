"""This module defines helper function that deals with account validation."""


from ng.models import Account
from ng.http import HttpResponse, HttpRedirectResponse
import _sessionhelper


class InvalidSessionException(Exception):
    """Exception that is raised when failed to extract valid account from
    session."""

    def __init__(self, response):
        """Create invalid session exception with the HTTP response that
        should be should be returned."""
        self.response = response


def get_session_account(request, db):
    """Try to extract account signed in from the request. Return Account
    object if successful. Raise InvalidSessionException if failed."""
    # Get session from database
    session = _sessionhelper.get_session(request, db)

    # Redirect request to sign in page if session doesn't exist
    if session is None:
        raise InvalidSessionException(HttpRedirectResponse('/signin'))

    # Redirect request to sign in page and expire cookie if session is
    # invalid
    uid = session.get_attribute('UID')
    if session.expired() or not uid:
        session.invalidate()
        cookie = _sessionhelper.expire_cookie_for_session(
            session,
            '/',
            request.server_name
        )
        response = HttpRedirectResponse('/signin')
        response.set_cookie(cookie)
        raise InvalidSessionException(response)

    # Redirect request to sign in page and expire cookie if uid is invalid
    account = Account.load_from_database(db, uid=uid)
    if account is None:
        session.invalidate()
        cookie = _sessionhelper.expire_cookie_for_session(
            session,
            '/',
            request.server_name
        )
        response = HttpRedirectResponse('/signin')
        response.set_cookie(cookie)
        raise InvalidSessionException(response)

    return account
