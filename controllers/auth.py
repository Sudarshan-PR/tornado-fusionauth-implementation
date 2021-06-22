import urllib.parse

import tornado.web
import tornado.auth
from tornado import escape
from tornado.httputil import url_concat

import casbin

import settings

# Returns a list of permissions from casbin
def get_permissions(role, userid):
    e = casbin.Enforcer('utils/model1.conf', 'utils/policy1.csv')
    
    objects = [
        'configurationsettings', 'changesettings', 'socialmediaauth', 'createuser', 'public_posts_and_emails', 'privatemessages', 
        'editposts', 'emailticket', 'deletefromsocialinbox', 'publicdomainrespond','publishbrandposts', 'createcustomreport', 
        'agentperfreport', 'agentauditreport', 'usermonitoringreport', 'assigntickets', 'accesssToCXAgentTickets', 'allaccesstickets',
    ]
    
    perms = []

    for obj in objects:
        sub = {
            'Role':role,
            'Userid':userid,
        }
        action = 'write'
        if (e.enforce(sub,obj,action)):
            perms.append(obj)

    return perms

class FushionAuthOauth2Mixin(tornado.web.RequestHandler, tornado.auth.OAuth2Mixin):
    clientid = settings.fusionauth_client_id
    _OAUTH_AUTHORIZE_URL = 'http://localhost:9011/oauth2/authorize'
    _OAUTH_ACCESS_TOKEN_URL = 'http://localhost:9011/oauth2/token'
    _FUSIONAUTH_USER_URL = 'http://localhost:9011/oauth2/userinfo'
    _FUSIONAUTH_LOGOUT_URL = f'http://localhost:9011/oauth2/logout?client_id={clientid}'

    # Get access_token, refresh_token, id_token & expires_in
    async def _get_tokens(self):
        http = self.get_auth_http_client()

        # Post Parameters (Data/Body)
        post_args = {
            'redirect_uri': 'http://localhost:8000/callback',
            'client_id': settings.fusionauth_key,
            'client_secret': settings.fusionauth_secret_key,
            'code': self.get_argument('code'),
            'grant_type': 'authorization_code',
        }

        response = await http.fetch(
            self._OAUTH_ACCESS_TOKEN_URL,
            method="POST",
            body=urllib.parse.urlencode(post_args)
        )

        # Decode json response to python dict and return
        return escape.json_decode(response.body)

    async def get_user_info(self, access_token):
        http = self.get_auth_http_client()

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = await http.fetch(
            self._FUSIONAUTH_USER_URL,
            headers=headers
        )

        return escape.json_decode(response.body)

    def fusionauth_logout(self):
        return self._FUSIONAUTH_LOGOUT_URL

class FushionAuthLoginController(FushionAuthOauth2Mixin):
    async def get(self):
        # Callback handler (FusionAuth Callback)
        if self.get_argument('code', False):
            token = await self._get_tokens()
            print("Token: " + str(token)) 
            # Get user data from FusionAuth using the access token
            user = await self.get_user_info(token['access_token'])            
            
            # Get username
            if user.get('given_name'):
                username = user['given_name']
            elif user.get('preferred_username'):
                username = user['preferred_username']
            
            # Get the user's first role
            role = user['roles'][0]

            # Get a user's permissions
            permissions = get_permissions(role, username)
            # Stringify permissions array
            permissions = escape.json_encode(permissions)

            # Set permissions and access_token as cookies
            self.set_secure_cookie("permissions", permissions)
            self.set_secure_cookie("access_token", token['access_token'])

            self.redirect('/')

        # If not logged in, redirect to Fusionauth Login Page
        else:
            self.authorize_redirect( 
                redirect_uri = 'http://localhost:8000/callback',
                client_id = settings.fusionauth_key,
                client_secret = settings.fusionauth_secret_key,
                scope = ['profile', 'email', 'openid'],
                response_type = "code"
            )

# Clear all cookies
class LogoutController(FushionAuthOauth2Mixin):
    async def get(self):
       logout_url = self.fusionauth_logout()
       self.clear_cookie("access_token")
       self.redirect(logout_url)
