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


def code_description(http_code):
    """Return description of a specified http status code."""
    if http_code in _http_status_code:
        return _http_status_code[http_code]
    else:
        return 'Unknown Status Code'


def code_status(http_code):
    """Return the status header of the code."""
    return '%d %s' % (http_code, code_description(http_code))


def test():
    print code_description(404)
    print code_description(100)


if __name__ == '__main__':
    test()
