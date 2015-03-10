"""Constructor of HTTP response"""

import sys

class View(object):

    """Abstract View class"""

    headers = { 'Content-Type' : "text/plain" }

    def __init__(self, headers = None):
        """Create an empty view with extra headers."""
        if headers:
            self.headers.update(headers)

    def write_to_output(self, out = None):
        """Write this view to output. out is the specified output file.
        If out is None, stdout will be used."""
        # Use stdout if output file is not specified
        if not out:
            out = sys.stdout

        header_list = ['%s: %s' % (key, value) for key, value in self.headers.items()]
        headers_str = '\r\n'.join(header_list)

        out.write(headers_str)
        out.write('\r\n\r\n')
        out.flush()

def test_View():
    print 'Emtpy view:'
    empty_view = View()
    empty_view.write_to_output()

    print 'Header view:'
    header_view = View({
            'Content-Type' : "text/html",
            'Set-Cookie' : 'ID=1',
        })
    header_view.write_to_output()

    print 'To file:'
    with open('/tmp/view', 'w') as tmp_file:
        header_view.write_to_output(tmp_file)

if __name__ == '__main__':
    test_View()
