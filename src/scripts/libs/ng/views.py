"""Constructor of HTTP response"""

import sys


class View(object):
    """Empty view that only contains headers"""

    def __init__(self, headers=None):
        """Create an empty view with extra headers."""
        self.headers = {'Content-Type': "text/plain"}
        if headers:
            self._add_headers(headers)

    def _add_headers(self, headers):
        """Add extra headers to self.headers"""
        for key, value in headers.items():
            # If the value is a list, add it to the original list
            if isinstance(value, list):
                if key in self.headers:
                    self.headers[key] = self.headers[key] + value
                else:
                    self.headers[key] = value
            else:
                self.headers[key] = value

    def add_headers(self, headers):
        """Add extra headers to this view"""
        if headers:
            self._add_headers(headers)

    def remove_header(self, header_name):
        """Remove the specified header from this view"""
        if header_name in self.headers:
            del self.headers[header_name]

    def _write_headers(self, out):
        """Write headers of this view to output file."""
        # Construct header string
        header_list = []
        for key, value in self.headers.items():
            # If there is multiple values for one key,
            # create item for each value
            if isinstance(value, list):
                for item in value:
                    header_list.append('%s: %s' % (key, item))
            else:
                header_list.append('%s: %s' % (key, value))
        headers_str = '\r\n'.join(header_list)

        # write header string to output file
        out.write(headers_str)
        out.write('\r\n\r\n')

    def write_to_output(self, out=None):
        """Write this view to output. out is the specified output file.
        If out is not specified, stdout will be used."""
        # Use stdout if output file is not specified
        if not out:
            out = sys.stdout

        self._write_headers(out)
        out.flush()


def test_View():
    print 'Emtpy view:'
    empty_view = View()
    empty_view.write_to_output()

    print 'Header view:'
    header_view = View({
            'Content-Type': "text/html",
            'Content-Length': '123',
        })
    header_view.add_headers({'Set-Cookie': ['ID=1', 'Session=foo']})
    header_view.remove_header('Content-Length')
    header_view.write_to_output()

    print 'To file:'
    with open('/tmp/view', 'w') as tmp_file:
        header_view.write_to_output(tmp_file)

if __name__ == '__main__':
    test_View()
