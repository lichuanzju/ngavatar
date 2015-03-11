"""This module defines a series of views that generates HTTP responses."""

import sys
import os
import errno
from excepts import HttpError
from excepts import FileLocateError
from excepts import FileReadError
from excepts import FileWriteError


class View(object):
    """Empty view that only contains headers."""

    def __init__(self, headers=None):
        """Create an empty view with extra headers."""
        self.headers = {'Content-Type': "text/plain"}
        if headers:
            self._add_headers(headers)

    def _add_headers(self, headers):
        """Add extra headers to self.headers."""
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
        """Add extra headers to this view."""
        if headers:
            self._add_headers(headers)

    def remove_header(self, header_name):
        """Remove the specified header from this view."""
        if header_name in self.headers:
            del self.headers[header_name]

    def _get_header_string(self):
        """Return the http header of this view."""
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

        return headers_str

    def _render_with_file(self, filepath, text_mode):
        """Render the body of this view with specified file.
        text_mode should be True if the file is a text file."""
        # Set file open mode
        if text_mode:
            open_mode = 'r'
        else:
            open_mode = 'rb'

        # Try to read file
        input_file = None
        try:
            input_file = open(filepath, open_mode)
            file_content = input_file.read()
        except IOError as e:
            if e.errno == errno.ENOENT:
                raise FileLocateError(filepath)
            else:
                raise FileReadError(filepath)
        finally:
            if input_file:
                input_file.close()

        return file_content

    def _render_with_text_file(self, filepath):
        """Render the body of this view with a text file."""
        return self._render_with_file(filepath, True)

    def _render_with_binary_file(self, filepath):
        """Render the body of this view with a binary file."""
        return self._render_with_file(filepath, False)

    def _render_body(self):
        """Render the body of this view."""
        return ''

    def render(self):
        """Render this view. Tuple (header, body) is returned."""
        body = ''
        try:
            body = self._render_body()
        except HttpError as e:
            self.headers.clear()
            self.headers['Status'] = e.http_status()

        header = self._get_header_string()

        return header, body

    def write_to_output(self, out=None):
        """Write this view to out file. If out file is not specified,
        stdout is used."""
        if not out:
            out = sys.stdout

        header, body = self.render()

        out.write(header)
        out.write('\r\n\r\n')
        out.write(body)
        out.flush()


class StaticView(View):
    """View that displays the content of a static html file."""

    def __init__(self, filepath):
        """Create a static view with path to the html file."""
        self.headers = {'Content-Type': 'text/html'}
        self.filepath = filepath

    def _render_body(self):
        """Render the body of this view with static html file."""
        return self._render_with_text_file(self.filepath)


class ImageView(View):
    """View that displays an image."""

    def __init__(self, image_path, image_format=None):
        """Create an image view with path and format of the image file."""
        self.filepath = image_path

        if not image_format:
            file_extension = os.path.splitext(image_path)[1]
            if not file_extension:
                file_extension = 'jpeg'

            import _image_extension_to_format
            image_format = _image_extension_to_format.\
                image_format_from_extension(file_extension)

        content_type = "image/" + image_format
        self.headers = {'Content-Type': content_type}

    def _render_body(self):
        """Render the body of this view with image file."""
        return self._render_with_binary_file(self.filepath)


class BinaryDataView(View):
    """View that send a binary file to client."""

    def __init__(self, filepath):
        """Create a binary data view with path to the binary file."""
        self.filepath = filepath

        # Get Content-Disposition header from filename
        filename = os.path.basename(filepath)
        content_disposition = 'attachment; filename="%s"' % filename

        self.headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': content_disposition,
        }

    def _render_body(self):
        """Render the body of this view with binary file."""
        return self._render_with_binary_file(self.filepath)


class TemplateFormatError(HttpError):
    """Error that is raised when format of a template is illegal."""

    def __init__(self, template_filepath, reason=None):
        """Create template format error with path to the file."""
        HttpError.__init__(self, 500)
        self.template_filepath = template_filepath
        self.reason = reason

    def __str__(self):
        """Return description of this error."""
        return 'Template file "%s" has illegal format: %s' %\
            (self.template_filepath, self.reason)


class TemplateView(View):
    """View that displays html loaded from a template."""

    def __init__(self, template_filepath, template_arguments):
        """Create template view with path to template file
        and arguments to evaluate template."""
        self.filepath = template_filepath
        self.headers = {'Content-Type': 'text/html'}
        self.template_arguments = template_arguments

    def _render_body(self):
        """Render the body of this view with template file and arguments."""
        # Load template
        import _template_loader
        html_string = _template_loader.load_template(
            self.filepath,
            self.template_arguments
        )

        return html_string


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
    print 'The view has been written to /tmp/view'


def test_StaticView():
    print 'Static View:'

    with open('/tmp/static.html', 'w') as html_file:
        html_file.write("<html>\n</html>")

    static_view = StaticView('/tmp/static.html')
    static_view.write_to_output()


def test_ImageView():
    print "Image View:"

    image_view = ImageView('/tmp/image.png')
    with open('/tmp/imageview', 'wb') as tmp_file:
        image_view.write_to_output(tmp_file)

    print "The view has been written to /tmp/imageview"


def test_BinaryDataView():
    print "Binary Data View:"

    binary_view = BinaryDataView('/tmp/image.png')
    with open('/tmp/binarydataview', 'wb') as tmp_file:
        binary_view.write_to_output(tmp_file)

    print "The view has been written to /tmp/binarydataview"


def test_TemplateView():
    print "Template View:"

    template_arguments = {
        'namespace': 'http://www.w3.org/1999/xhtml',
        'title': 'ngavatar',
        'body': '<h2>Welcome</h2>',
    }
    template_view = TemplateView('/tmp/template.html', template_arguments)
    template_view.write_to_output()


if __name__ == '__main__':
    test_View()
    test_StaticView()
    test_ImageView()
    test_BinaryDataView()
    test_TemplateView()
