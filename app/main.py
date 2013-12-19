'''
This is the main app file
Code is available here: https://github.com/zugaldia/cartoglass
'''

# Libraries provided by Python/App Engine (see app.yaml)
# Note this is easily portable to other cloud services (users -> oauth2)
from google.appengine.api import users
from google.appengine.ext import db
from random import randint
import jinja2
import json
import logging
import webapp2

# Libraries included in the packages folder
from apiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator, StorageByKeyName, CredentialsProperty
import httplib2
import requests

# Our secret credentials, DO NOT include this in GitHub
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, CARTODB_API_KEY

# Set up Jinja2's environment (template system) with default values and
# folder `templates` as the root for our HTML templates
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'))

# Scopes for OAuth2 (authorization)
GOOGLE_SCOPES = [
    # These are the two scopes related to Glass, we'll use both:
    'https://www.googleapis.com/auth/glass.timeline',
    'https://www.googleapis.com/auth/glass.location',
    # Include this two if you need more information about the user,
    # or any other Google OAuth2 scope (drive, google+, ...)
    # 'https://www.googleapis.com/auth/userinfo.email',
    # 'https://www.googleapis.com/auth/userinfo.profile'
]

# This decorator handle all of the OAuth 2.0 steps without you having to use
# any Flow, Credentials, or Storage objects.
decorator = OAuth2Decorator(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    scope=GOOGLE_SCOPES,
    # Forces to get a refresh token, fixes { "error" : "invalid_grant" }
    # approval_prompt='force'
)

# The model where we'll store the credentials
class CredentialsModel(db.Model):
    credentials = CredentialsProperty()

# We'll use this to execute all calls to the Mirror API
service = build('mirror', 'v1')

class MainHandler(webapp2.RequestHandler):
    def get(self):
        # Render the template, this could be moved to a base RequestHandler
        # as described here:
        # http://webapp-improved.appspot.com/api/webapp2_extras/jinja2.html
        template = jinja_environment.get_template('landing.html')
        self.response.write(template.render())

class InstallHandler(webapp2.RequestHandler):
    # One line of code to handle the OAuth2 dance
    @decorator.oauth_required
    def get(self):
        # Get the authorized HTTP object created by the decorator.
        # @decorator.oauth_aware gives you more control of the flow if needed
        self.http = decorator.http()

        # You could use the user_id to keep track of per user installs
        self.user_id = users.get_current_user().user_id()

        # It's always a good idea to surround API calls with try/except/else
        try:
            # Once we have proper authorization we're gonna carry out three tasks:
            # (these tasks could be moved to a GlassService class, and benefit from
            # batch requests.)
            self._send_welcome_card()
            self._subscribe_to_timeline()
            self._subscribe_to_location()
        except Exception as e:
            logging.error('Install failed: %s' % str(e))
            all_good = False
        else:
            all_good = True

        # Render the template
        template = jinja_environment.get_template('install.html')
        self.response.write(template.render({'all_good': all_good}))

    def _send_welcome_card(self):
        # Body of the request
        # If this gets too complicated, you could create a wrapping class
        body = {
            # Describes how important the notification is. DEFAULT is the only
            # allowed value.
            'notification': {'level': 'DEFAULT'},
            # A speakable description of the type of this item. This will be
            # announced to the user prior to reading the content of the item
            # in cases where the additional context is useful, for example
            # when the user requests that the item be read aloud following a
            # notification.
            'speakableType': 'Welcome card',
            # This accompanies the read aloud menu item
            'speakableText': 'You can\'t see me, but you can hear me',
            # This is the most basic way of providing content, it looks great
            # in many situations (ignored if you use HTML content). It
            # auto-resizes according to the text length.
            'text': 'Hello Glassingtonian!',
            # You can use the playground to see how it's gonna look like:
            # (pretty close to the text before, but with Glassingtonian in bold yellow)
            # https://developers.google.com/glass/playground. And the CSS:
            # https://mirror-api-playground.appspot.com/assets/css/base_style.css
            'html': '<article><section><p class="text-auto-size">Hello '
                    '<strong class="yellow">Glassingtonian</strong>!</p></section></article>',
            # Normally you won't need so many items, this just for demo purposes
            'menuItems': [
                # These are all built-in (free implementation) actions
                { 'action': 'READ_ALOUD' },
                { 'action': 'TOGGLE_PINNED' },
                { 'action': 'DELETE' },
                # Built-in actions with a payload (note the READ_ALOUD inconsinstency)
                { 'action': 'OPEN_URI',
                  'payload': 'http://www.techmeme.com' },
                { 'action': 'PLAY_VIDEO',
                  'payload': 'https://cartoglass.appspot.com/static/video.mp4' },
                # This is how you define a custom action
                { 'action': 'CUSTOM',
                  'id': 'GUESS_A_NUMBER',
                  'values': [ {
                        'displayName': 'Guess a number',
                        'iconUrl': 'https://cartoglass.appspot.com/static/glyphicons_009_magic.png',
                        # You can also include states for PENDING and CONFIRMED
                        'state': 'DEFAULT'
                    }]
                }
            ]
        }

        # Authenticated request
        response = service.timeline().insert(body=body).execute(http=self.http)
        logging.info(response)

    def _subscribe_to_timeline(self):
        # Body of the request
        body = {
            'collection': 'timeline',
            # A secret token sent to the subscriber in notifications so that
            # it can verify that the notification was generated by Google.
            'verifyToken': 'I_AM_YOUR_FATHER',
            # An opaque token sent to the subscriber in notifications so that
            # it can determine the ID of the user. You could obfuscate this
            # value for increased security
            'userToken': self.user_id,
            # Notice the HTTPS. This won't work for localhost eiter.
            # During development, you use the subscription proxy:
            # https://developers.google.com/glass/subscription-proxy
            'callbackUrl': 'https://cartoglass.appspot.com/subscription'
        }

        # Authenticated request
        response = service.subscriptions().insert(body=body).execute(http=self.http)
        logging.info(response)

    def _subscribe_to_location(self):
        # Same as timeline, only replacing the `collection` name
        body = {
            'collection': 'locations',
            'verifyToken': 'I_AM_YOUR_FATHER',
            'userToken': self.user_id,
            'callbackUrl': 'https://cartoglass.appspot.com/subscription'
        }

        # Authenticated request
        response = service.subscriptions().insert(body=body).execute(http=self.http)
        logging.info(response)

class SubscriptionHandler(webapp2.RequestHandler):
    # Note it comes as a POST request. If you fail to respond, the mirror API
    # will retry up to 5 times.
    def post(self):
        data = json.loads(self.request.body)

        # Returns a 403 Forbidden (authenticating will make no difference)
        if data.get('verifyToken') != 'I_AM_YOUR_FATHER':
            logging.error('Unauthorized request to the subscription endpoint.')
            return self.abort(403)

        # Get the credentials, you could also check credentials.refresh_token is not None
        self.user_id = data.get('userToken')
        credentials = StorageByKeyName(CredentialsModel, self.user_id, 'credentials').get()
        if not credentials:
            logging.error('Authentication is required and has failed.')
            return self.abort(401)

        # http was previously authorized by the decorator
        self.http = credentials.authorize(httplib2.Http())

        try:
            # Handle the appropriate type of subscription
            if data.get('collection') == 'locations':
                self._handle_location(data)
            elif data.get('collection') == 'timeline':
                self._handle_timeline(data)
        except Exception as e:
            logging.error('Failed SubscriptionHandler for user_id %s: %s',
                (self.user_id, str(e)))

    def _handle_location(self, data):
        # Note 1: You still need another request to get the actual location

        # Note 2: The courtesy limit is 1,000 requests/day and you may get
        # around 1 notification per user every 10 minutes. That means you 
        # should NOT do this every single time, otherwise, you'll be over the
        # limit when you reach ~ 7 users (1,000 / 24 * 6).

        response = service.locations().get(id=data.get('itemId')).execute(http=self.http)
        logging.info(response)

        # Note 3: Slight inconsistency with Android (address, speed, altitude, types)
        # Location in Glass has the following fields:
        #   timestamp: datetime,
        #   latitude: double,
        #   longitude: double,
        #   accuracy: double,
        #   displayName: string,
        #   address: string
        # In Android, however, android.location.Location has the following methods:
        #   getAccuracy(): float
        #   getAltitude(): double
        #   getBearing(): float
        #   getElapsedRealtimeNanos(): long
        #   getLatitude(): double
        #   getLongitude(): double
        #   getProvider(): String
        #   getSpeed(): float
        #   getTime(): long

        # Store the values in CartoDB
        values = {'longitude': response.get('longitude'),
                  'latitude': response.get('latitude'),
                  'accuracy': response.get('accuracy'),  # in meters
                  # Remove the single quote to respect the query format below
                  'address': response.get('address', '').replace("'", ""),
                  'display_name': response.get('displayName', '').replace("'", ""),
                  'user_id': self.user_id }

        payload = {
            'api_key': CARTODB_API_KEY,
            # This is a plain PostgreSQL query
            'q': "INSERT INTO cartoglass (the_geom, accuracy, address, displayname, user_id) "
                 "VALUES (ST_GeomFromText('POINT({longitude} {latitude})', 4326), "
                 "{accuracy}, '{address}', '{display_name}', '{user_id}');".format(**values)
        }

        # Use Requests
        r = requests.get('http://zugaldia.cartodb.com/api/v2/sql', params=payload)
        logging.info('CartoDB: %s (response: %s, query: %s)' %
            (r.status_code, r.text, payload['q']))

    def _handle_timeline(self, data):
        # A list of actions taken by the user that triggered the notification.
        for user_action in data.get('userActions', []):
            # The user selected the custom menu item in the timeline item
            if (user_action.get('type') == 'CUSTOM' and
                user_action.get('payload') == 'GUESS_A_NUMBER'):

                # You could carry out some server-side action here, hopefully
                # more interesting than generating a random number.
                random_number = randint(1, 10)

                # We insert a card with a randon mumber as the user response
                body = {
                    'notification': {'level': 'DEFAULT'},
                    'speakableType': 'This is so random',
                    'text': 'This is the number I had in mind: ' + str(random_number),
                    'menuItems': [{ 'action': 'DELETE' }]
                }

                # Authenticated request
                response = service.timeline().insert(body=body).execute(http=self.http)
                logging.info(response)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/install', InstallHandler),
    # Glass will notify you of timeline actions and location updates
    # through this endpoint:
    ('/subscription', SubscriptionHandler),
    # This will take care of the OAuth2 callback redirect for you
    # See: https://developers.google.com/api-client-library/python/guide/google_app_engine
    (decorator.callback_path, decorator.callback_handler()),
    # You should provide an uninstall handler as part of the developer
    # policies and give users a reasonably convenient way to delete any of
    # their personal information you've obtained from the API.
    #('/uninstall', UninstallHandler)
], debug=True)
