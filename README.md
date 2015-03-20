# NGAVATAR

## Introduction
This project is a website designed to provide avatar management services. Users signed in to this website can add email addresses, upload avatars and set avatars for each of their own email addresses. Other websites can get the avatars for email addresses from this site through a public API.

## Installation
To install this website and make it available on your server, please go through the following instructions.  

### For automatic installation:
1. Login into a Debian like operation system.
2. Use `apt-get` to install the following packages: `apache2`, `python2.7`, `mysql`, `mysql-dev`, `mysql-python`.
3. Enable cgid mod for apache server.
4. Create a directory to hold all the files of the site.
5. Run tools/install.sh with root privileges (**Please be noted that there is no self-cleaning procedure in the script. So you must be careful with the arguments and make sure you can undo the script operations manually.** Use '-h' option to get usage.). The bash script will ask for the following parameters:
    i. The path to the root directory of this site.
    ii. The listening port number of this site.
    iii. The name of the Apache2 configuration file.
    iv. The host name of the MySQL server.
    v. The port number of the MySQL server.
    vi. The root password of the MySQL server.

### For manual installation:
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

## Uninstallation
To clean the installation of this website, please go through the following steps:

1. Remove all files from the root directory.
2. Remove ngavatar.pth file from the python `site-packages`(`dist-packages`) directory.
3. Remove the apache site .conf file from the `sites-enabled` directory and delete port listening statement in the `ports.conf` file.
4. Drop schema `ngavatar` and user `ng` in your MySQL server.

## Project Structure
The file structure of this project:
```
├── docs                                    # Documents
│   └── ng                                  # Python doc for package ng
├── README.md
├── src                                     # Source code
│   ├── scripts
│   │   ├── cgi                             # CGI scripts and related modules
│   │   │   ├── config.py                   # Functions for loading config file
│   │   │   ├── gateway.cgi                 # The gateway CGI script
│   │   │   └── handlers                    # HTTP request handler functions
│   │   ├── conf                            # Configuration
│   │   │   └── ngavatar.conf               # The configuration file
│   │   ├── libs                            # Supporting libraries
│   │   │   └── ng                          # Python package ng
│   │   │       ├── database.py             # Database wrapper classes
│   │   │       ├── excepts.py              # Basic Exceptions
│   │   │       ├── httpfilters.py          # Decorators for handler functions
│   │   │       ├── http.py                 # HTTP related classes
│   │   │       ├── __init__.py
│   │   │       ├── models.py               # Data model classes
│   │   │       ├── str_generator.py        # String generate functions
│   │   │       ├── _template_loader.py     # Template loading functions
│   │   │       ├── views.py                # View classes
│   │   └── sql                             # SQL scripts
│   │       └── create_database.sql         # Script for initializing database
│   ├── static                              # Static HTML files
│   │   ├── 403.html                        # Page for 403 errors
│   │   ├── 404.html                        # Page for 404 errors
│   │   ├── 405.html                        # Page for 405 errors
│   │   ├── 500.html                        # Page for 500 errors
│   │   ├── icons
│   │   │   └── favicon.ico                 # The favicon for this site
│   │   └── images                          # Static images
│   │       ├── failed.png
│   │       └── successful.png
│   ├── storage                             # Directory to store serverside data
│   │   └── avatars                         # Avatars uploaded
│   └── templates                           # Template files
└── tools                                   # Tools for running this site
    ├── install.sh                          # The installation shell script
    └── ngavatar.conf                       # Apache2 site config template
```

## Design

### Modules
- Database module: database accessing classes created by wrapping MySQLdb
- Data models: model classes that provide data accessing functionality by wrapping database module
- Views: view classes that generates body of HTTP responses
- HTTP module: classes that wraps HTTP protocol related data, such as requests, responses, cookies and sessions
- HTTP request handlers: functions that take HTTP requests and generate HTTP responses
- CGI gateway script: the only CGI script that dispatches HTTP requests to designated handler functions

### Data Flow
The data flow of this project is as follows:
```
     MySQLdb <--> MySQLDatabase <--> Data models
                                        ^
                                        |
                                        v
  gateway.cgi --> HttpRequest --> Handler functions --> HttpResponse --> Apache2
                                        ^
                                        |
                                        |
               Template files -------> Views <-------- Static files
```

1. The gateway.cgi script create HttpRequest object from CGI input variables and load the configuration file;
2. The gateway.cgi script get the handler function from the request URL and pass HttpRequest and configuration to it;
3. The handler function generates HttpResponse object with data models and views;
    i. Data models manipulate data by calling database API provided by database module;
    ii. Views generate HTTP response body by loading template files and static files;
4. The gateway.cgi get the HttpResponse object returned by the handler function and write it to the CGI output.

### Database module
Database module defines classes that provide database API.

1. Database class: base class that defines common database operations.
2. MySQLDatabase class: class than implements operations defined in Database class calling APIs provided by mysql-python package.

### Data Models
Data models represent data instances stored in this site, which includes the following classes:

1. DatabaseModel: base class that defines model operations such loading, storing, deleting etc. These operations are implemented by calling the functionalities provided by the database module.
2. Account: model that stores information of user accounts.
3. Avatar: model that stores information of avatars uploaded by users.
4. Email: model that stores information of email addresses added by users.
5. Session: model that holds data and attributes of HTTP session.

### Views
View classes generate the body of HTTP responses by loading static html files, image files, binary files and template files.

1. View: base class that defines the interface of view classes.
2. StaticView: view that generates the body by reading the content of static files.
3. ImageView: view that generates the body by reading data from image files.
4. BinaryView: view that generates the body by reading data from binary files.
5. TemplateView: view that generates the body by loading and evaluating template files.

### HTTP module
HTTP module defines classes that related to HTTP protocol, including:

1. HttpCookie: class that stores attributes of an HTTP cookie.
2. HttpRequest: class that holds all parameters of an HTTP request.
3. HttpResponse: class that holds headers and body(usually generated by views) of an HTTP response.
    i. HttpRedirectResponse: response that redirects a request to another location.
    ii. HttpErrorResponse: response that returns an http error status to the client.
4. HttpSession: class that defines interface of HTTP sessions.
5. DatabaseSession: session class that uses Session model to implement session interfaces.

### HTTP Request handlers
An HTTP request handler is a function that takes an HttpRequest object and returns an HttpResponse object. The handlers use HTTP module to parse requests and construct responses. Data models are used by handlers to load and store data. Views are used by handlers to form response bodies.

### CGI gateway script
The gateway script is an executable python script that processes all HTTP requests passed by the web server except static file requests. It processes the request through the following steps:

1. Create HttpRequest object from environment variables.
2. Create configuration data by loading the configuration file.
3. Lookup the handler table and get the handler function according the URL of the request.
4. Call the handler function with the request object and configuration data.
5. Get the HttpResponse object returned by the handler function and write it to output.
6. If any exceptions raised during the above steps, generate an corresponding HttpErrorResponse object and write it to the output.

### Error handling
- There are 2 kinds of exceptions that may be raised in this project: HTTP errors and other errors.
- HTTP errors are errors that raised in purpose to inform the gateway CGI script to generate a response with HTTP error statuses. These errors are caused by unfounded resources, illegal requests and illegal template formats etc.
- Other errors are errors that raised unexpectedly by certain python code with bugs. If any of these errors are catched by the gateway script, an HTTP 500 error status will be returned to the client.

## Other documents
If you are interested in the detailed implementation of this project, please read the documents in the `docs` directory.
