"""This package provides configuration loading utilities. By importing
this package, the configuration file will be loaded automatically and
stored in the package global variable SITE_CONF"""


import os
from ng.excepts import HttpError


class ConfigurationLoadError(HttpError):
    """Error that is raised when failed to load configuration."""

    def __init__(self, conf_filepath):
        """Create configuration load error with path to conf file."""
        HttpError.__init__(self, 500)
        self.conf_filepath = conf_filepath

    def __str__(self):
        """Return description of this error."""
        return 'Failed to load configuration file "%s"' % \
            self.conf_filepath


def _load_configuration(conf_filepath):
    """Load configuration from file and return it as a dictionary."""
    global_ = {}
    try:
        execfile(conf_filepath, global_)
    except:
        raise ConfigurationLoadError(conf_filepath)

    return global_


def template_filepath(template_filename):
    """Return the absolute path to a template file."""
    if not template_filename:
        return None

    return os.path.join(SITE_CONF.get('template_path', ''),
                        template_filename)


def static_filepath(static_filename):
    """Return the absolute path to a static file."""
    if not static_filename:
        return None

    return os.path.join(SITE_CONF.get('static_path', ''),
                        static_filename)


def storage_filepath(storage_filename):
    """Return the absolute path to a storage file."""
    if not storage_filename:
        return None

    return os.path.join(SITE_CONF.get('storage_path', ''),
                        storage_filename)


# Get absolute path for configuration file
_conf_relative_filepath = '../conf/ngavatar.conf'
_current_path = os.path.dirname(os.path.realpath(__file__))
_conf_filepath = _current_path + '/' + _conf_relative_filepath

# Set the package global variable
SITE_CONF = _load_configuration(_conf_filepath)
