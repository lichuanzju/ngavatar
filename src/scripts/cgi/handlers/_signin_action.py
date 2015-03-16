"""This module defines handler that handles /signup_action requests."""


from ng import httpfilters
from ng.database import MySQLDatabase
from ng.http import HttpCookie, DatabaseSession
from ng.http import HttpResponse, HttpRedirectResponse
from ng.models import Account
from ng.views import TemplateView
import config


def failed_response(error_message, conf):
    """Generate sign in error page with specified error message."""
    template_args = dict(
        error_message=error_message,
        site_name=conf.get('name', '')
    )

    failed_view = TemplateView(
        config.template_filepath('signin_failed.html'),
        template_args
    )

    return HttpResponse(failed_view)


@httpfilters.allow_methods('POST')
def handler(request, conf):
    """The handler function."""
    # Get username and password submitted
    username = request.field_storage.getvalue('username')
    password = request.field_storage.getvalue('password')

    # Check username availabibity
    if not username:
        return failed_response('please input your username', conf)

    # Check password availability
    if not password:
        return failed_response('please input your password', conf)

    # Connect database and do sign in action
    with MySQLDatabase(conf.get('database_connection')) as db:
        # Check username existance in database
        if not Account.username_exists(db, username):
            return failed_response('username %s does not exist' % username,
                                   conf)

        # Load the account information from database
        account = Account.load_from_database(db, username=username)
        if account is None or account.get('uid') is None:
            return failed_response('username %s does not exist' % username,
                                   conf)
        uid = account.get('uid')

        # Check password correctness
        if not account.check_password(password):
            return failed_response('password incorrect', conf)

        # Create a new session in database
        session_data = dict(UID=uid)
        session = DatabaseSession.create_session(
            db,
            session_data,
            request.client_addr,
            conf.get('session_effective_hours', 72)
        )

        # Check session
        if session is None:
            return failed_response('cannot create session')

        # Create cookie
        cookie_data = dict(SessionKey=session.get_session_key())
        cookie = HttpCookie(
            cookie_data,
            '/',
            session.get_expire_time(),
            request.server_name
        )

        # Create redirect response to /usermain
        response = HttpRedirectResponse('/usermain')
        response.add_headers({'Set-Cookie': cookie.http_header()})
        return response
