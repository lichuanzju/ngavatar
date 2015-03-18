"""This module defines the handler that handles avatar API requests from
other websites."""


from ng import httpfilters
from ng.database import MySQLDatabase
from ng.http import HttpResponse, HttpErrorResponse
from ng.models import Avatar, Email
from ng.views import TemplateView, ImageView, StaticView
import config
import _accounthelper


def http_error_response(error_code, conf):
    """Generate response that indicates an HTTP error."""
    error_page_path = config.static_filepath(
        conf['error_pages'].get(error_code)
    )
    error_view = StaticView(error_page_path)

    response = HttpErrorResponse(error_code, error_view)
    return response


def avatar_response(avatar, conf):
    """Generate response that shows the avatar image."""
    avatar_path = config.storage_filepath(avatar.get('file_path'))
    avatar_view = ImageView(avatar_path)
    return HttpResponse(avatar_view)


@httpfilters.allow_methods('GET')
def handler(request, conf):
    """The handler function."""
    # Get email hash
    email_hash = request.field_storage.getvalue('email_hash')
    if not email_hash:
        return http_error_response(404, conf)
    email_hasn = email_hash.lower()

    with MySQLDatabase(conf.get('database_connection')) as db:
        # Load email with the hash from database
        email = Email.load_from_database(db, email_hash=email_hash)
        if email is None or email.get('avatar_id') is None:
            return http_error_response(404, conf)

        # Find the avatar that is set to the email
        aid = email.get('avatar_id')
        avatar = Avatar.load_from_database(db, aid=aid)
        if avatar is None:
            return http_error_response(404, conf)

        return avatar_response(avatar, conf)
