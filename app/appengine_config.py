'''
Google App Engine provides a mechanism allowing users to specify their own
values for constants and "hook functions" for use by some App Engine modules.
Specifying your own values can change the default behavior of those modules
based on the application's needs. The file where you specify these constants
is appengine_config.py. After creating this file, you simply deploy it with
your other code.

We're using this file to enable the `packages` folder for our third-party
components (Google APIs Client Library and Requests).

See the following link for more info:
https://developers.google.com/appengine/docs/python/tools/appengineconfig
'''

import os
import sys

vendor_dir = os.path.join(os.path.dirname(__file__), 'packages')
sys.path.append(vendor_dir)
