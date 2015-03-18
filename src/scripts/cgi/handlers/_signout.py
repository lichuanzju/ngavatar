"""This module defines handler that handles /signout requests."""


import datetime
from ng import httpfilters
from ng.database import MySQLDatabase
from ng.http import HttpResponse, HttpRedirectResponse, HttpCookie
from ng.views import TemplateView
import config
import _sessionhelper


@httpfilters.allow_methods('GET')
def handler(request, conf):
    """The handler function."""
    # Redirect this request to sign in page
    response = HttpRedirectResponse('/signin')

    with MySQLDatabase(conf.get('database_connection')) as db:
        # Get session from database
        session = _sessionhelper.get_session(request, db)

        # Remove session from database and generate session expiring cookie
        if session is not None:
            session.invalidate()
            cookie = _sessionhelper.expire_cookie_for_session(
                session,
                '/',
                request.server_name
            )
            response.set_cookie(cookie)

    return response
