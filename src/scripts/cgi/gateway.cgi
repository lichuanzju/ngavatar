#!/usr/bin/env python

import os

print "Content-Type: text/html\r\n\r\n"
print "<font size=+1>Environment</font><br/>"
for param in os.environ.keys():
    print "<b>%20s</b>: %s<br/>" % (param, os.environ[param])
