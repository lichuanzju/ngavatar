"""This module defines the handler that handlers /signin request."""


from ng import httpfilters
from ng.database import MySQLDatabase
from ng.http import HttpResponse, HttpRedirectResponse
from ng.views import TemplateView
import config
import _session_check


@httpfilters.allow_methods('GET')
def handler(request, conf):
    """The handler function."""
    with MySQLDatabase(conf.get('database_connection')) as db:
        # Get session from database
        session = _session_check.get_session(request, db)

        # Check session, redirect request to /usermain if valid
        if session is not None:
            if session.expired():
                session.delete_from_database(db)
            else:
                return HttpRedirectResponse('/usermain')

    username = request.field_storage.getvalue('username', '')

    template_args = dict(
        site_name=conf.get('name', ''),
        username=username
    )

    signin_view = TemplateView(
        config.template_filepath('signin.html'),
        template_args
    )

    return HttpResponse(signin_view)
