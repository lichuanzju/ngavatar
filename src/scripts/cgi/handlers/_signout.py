"""This module defines handler that handles /signout requests."""


import datetime
from ng import httpfilters
from ng.database import MySQLDatabase
from ng.http import HttpResponse, HttpRedirectResponse, HttpCookie
from ng.views import TemplateView
import config
import _session_check


@httpfilters.allow_methods('GET')
def handler(request, conf):
    """The handler function."""
    # Redirect this request to sign in page
    response = HttpRedirectResponse('/signin')

    with MySQLDatabase(conf.get('database_connection')) as db:
        # Get session from database
        session = _session_check.get_session(request, db)

        # Remove session from database and generate expiring cookie
        if session is not None:
            session.invalidate()

            cookie_data = dict(SessionKey=session.get_session_key())
            cookie = HttpCookie(
                cookie_data,
                '/',
                datetime.datetime.now() - datetime.timedelta(1),
                request.server_name
            )

            response.add_header('Set-Cookie', cookie.http_header())

    return response
