# NGAVATAR

## Introduction
This project is a website designed to provide avatar management services. Users signed in to this website can add email addresses, upload avatars and set avatars for each of their own email addresses. Other websites can get the avatars for email addresses from this site through a public API.

## Installation
To install this website and make it available on your server, please go through the following instructions.  

- For automatic installation:
    1. Login into a Debian like operation system.
    2. Use `apt-get` to install the following packages: `apache2`, `python2.7`, `mysql`, `mysql-dev`, `mysql-python`.
    3. Enable cgid mod for apache server.
    4. Run tools/install.sh with root privileges (**Please be noted that there is no self-cleaning procedure in the script. So you must be careful with the arguments and make sure you can undo the script operations manually.** Use '-h' option to get usage.).

- For manual installation:
    1. Install `apache2`, `python2.7` and `mysql` in your OS.
    2. Install `mysql-python` package for your python2.7.
    3. Enable cgid mod for apache server.
    4. Create a directory to hold this website (refered as `$root_dir` in the following steps).
    5. Copy all directories in `src` to the `$root_dir`.
    6. Modify `$root_dir/scripts/conf/ngavatar.conf` to customize your configuration. The default value of `site_root` and `database_connection` must be replaced.
    7. Add read permissions to apache2 user (`www-data` in Debian) for all files and directories in `$root_dir`. Add write permissions to the apache2 user for the storage directory and all files in it.
    8. Create a .pth file that contains the line `$root_dir/scripts/libs` in your python2.7 `site-packages` (`dist-packages`) directory.
    9. Copy `tools/ngavatar.conf` to apache2 `sites-enabled` directory. Replace `DOC_ROOT` with `$root_dir` and `SITE_PORT` with the listening port of the site in the .conf file.
    10. Add listening port to the apache2 `ports.conf` file.
    11. Execute `src/scripts/sql/create_database.sql` in MySQL client (login as root).
    12. Restart apache2 server and visit http://localhost:port/ to verify.

## Cleaning
To clean the installation of this website, please go through the following steps:

1. Remove all files from the root directory.
2. Remove ngavatar.pth file from the python `site-packages`(`dist-packages`) directory.
3. Remove the apache site .conf file from the `sites-enabled` directory and delete port listening statement in the `ports.conf` file.
4. Drop schema `ngavatar` and user `ng` in your MySQL server.
