"""This module defines the handler that handlers /signin request."""


from ng import httpfilters
from ng.database import MySQLDatabase
from ng.http import HttpResponse, HttpRedirectResponse
from ng.views import TemplateView
import config
import _sessionhelper


@httpfilters.allow_methods('GET')
def handler(request, conf):
    """The handler function."""
    cookie = None

    with MySQLDatabase(conf.get('database_connection')) as db:
        # Get session from database
        session = _sessionhelper.get_session(request, db)

        # Check session, redirect request to user main page if valid
        if session is not None:
            if session.expired():
                session.invalidate()
                cookie = _sessionhelper.expire_cookie_for_session(
                    session,
                    '/',
                    request.server_name
                )
            else:
                return HttpRedirectResponse('/user/main')

    username = request.field_storage.getvalue('username', '')

    template_args = dict(
        site_name=conf.get('name', ''),
        username=username
    )

    signin_view = TemplateView(
        config.template_filepath('signin.html'),
        template_args
    )

    response = HttpResponse(signin_view)
    response.set_cookie(cookie)
    return response
