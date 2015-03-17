"""This module defines helper function that deals with account validation."""


from ng.models import Account
from ng.http import HttpResponse, HttpRedirectResponse
import _sessionhelper

def check_signed_in(request, db):
    """Try to extract account signed in from the request. Return Account
    object if successful. Return HttpResonse object if failed."""
    # Get session from database
    session = _sessionhelper.get_session(request, db)

    # Redirect request to sign in page if session doesn't exist
    if session is None:
        return HttpRedirectResponse('/signin')

    # Redirect request to sign in page and expire cookie if session
    # is invalid
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
        return response

    # Redirect request to sign in page and expire cookie if uid is
    # invalid
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
        return response

    return account
