"""This module defines handler that handles /user/main requests."""


from ng import httpfilters
from ng.database import MySQLDatabase
from ng.models import Account, Email, Avatar
from ng.http import HttpResponse
from ng.views import TemplateView
import config
import _sessionhelper


def usermain_response(db, account, conf):
    """Generate response that shows user main page."""
    uid = account.get('uid')

    emails = Email.load_multiple_from_database(db, owner_uid=uid)
    avatars = Avatar.load_multiple_from_database(db, owner_uid=uid)

    template_args = dict(
        site_name=conf.get('name', ''),
        account=account,
        emails=emails,
        avatars=avatars
    )

    usermain_view = TemplateView(
        config.template_filepath('usermain.html'),
        template_args
    )

    return HttpResponse(usermain_view)


@httpfilters.allow_methods('GET')
def handler(request, conf):
    """The handler function."""
    with MySQLDatabase(conf.get('database_connection')) as db:
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

        return usermain_response(db, account, conf)
