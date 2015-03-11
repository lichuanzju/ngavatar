"""This module defines http status codes and their description."""

_http_status_code = {
    200: 'OK',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    500: 'Internal Server Error',
    501: 'Not Implemented',
}


def http_code_description(http_code):
    """Return description of a specified http status code."""
    if http_code in _http_status_code:
        return _http_status_code[http_code]
    else:
        return 'Unknown Status Code'


def test():
    print http_code_description(404)
    print http_code_description(100)


if __name__ == '__main__':
    test()
