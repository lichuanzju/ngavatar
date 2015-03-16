"""This module defines handler that handles the /index request."""


from ng import httpfilters
from ng.database import MySQLDatabase
from ng.http import HttpResponse
from ng.models import Account
from ng.views import TemplateView
import config
import _session_check


def index_response(conf, account=None):
    """Generate response that shows the page with no user signed in."""
    template_args = dict(
        site_name=conf.get('name', ''),
        account=account
    )

    index_view = TemplateView(
        config.template_filepath('index.html'),
        template_args
    )

    return HttpResponse(index_view)


@httpfilters.allow_methods('GET')
def handler(request, conf):
    """The handler function."""
    with MySQLDatabase(conf.get('database_connection')) as db:
        # Get session from database
        session = _session_check.get_session(request, db)

        # Check session, redirect request to /usermain if valid
        if session is None:
            return index_response(conf)

        # Check session expiring time
        if session.expired():
            session.invalidate()
            return index_response(conf)

        # Check session data
        uid = session.get_attribute('UID')
        if uid is None:
            return index_response(conf)

        # Load account
        account = Account.load_from_database(db, uid=uid)
        return index_response(conf, account)
