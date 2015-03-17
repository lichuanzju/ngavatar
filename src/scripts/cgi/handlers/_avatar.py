"""This module defines the handler that handles avatar image requests."""



from ng import httpfilters
from ng.database import MySQLDatabase
from ng.http import HttpResponse, HttpErrorResponse
from ng.models import Avatar
from ng.views import TemplateView, ImageView, StaticView
import config
import _accounthelper


def http_error_response(error_code, conf):
    """Generate response that indicates an http error."""
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
    with MySQLDatabase(conf.get('database_connection')) as db:
        # Try to get signed account
        account_or_response = _accounthelper.check_signed_in(request, db)
        if isinstance(account_or_response, HttpResponse):
            return http_error_response(403, conf)
        account = account_or_response

        # Check the id in the query string
        aid = request.field_storage.getvalue('id')
        if not aid:
            return http_error_response(404, conf)

        # Load the avatar instance from database
        avatar = Avatar.load_from_database(db,
                                           owner_uid=account.get('uid'),
                                           aid=aid)
        if avatar is None:
            return http_error_response(403, conf)

        return avatar_response(avatar, conf)
