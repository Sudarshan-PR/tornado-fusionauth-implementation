'''
    Read this guide first for a basic understanding of the lifecycle of MFA in fusionauth  https://fusionauth.io/docs/v1/tech/guides/multi-factor-authentication/

    Purpose of all the api-calls made in this code are explain here: https://fusionauth.io/docs/v1/tech/apis/two-factor/
'''

import urllib

import qrcode

import tornado.web
from tornado import escape
from tornado.httpclient import AsyncHTTPClient

from controllers.RequestHandler import BaseHandler

from settings import BASE_DIR, fusionauth_mgmt_key

http = AsyncHTTPClient()
api_key = fusionauth_mgmt_key

# Enable 2FA using Authenticator (TOTP) for a user
class EnableMFA(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        access_token = self.get_secure_cookie('access_token').decode('UTF-8')
        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        secrets = None
        # Generate Secrets
        url = 'http://localhost:9011/api/two-factor/secret'
        try:
            response = await http.fetch(
                url,
                headers=headers,
            )
            secrets = escape.json_decode(response.body)
            print(f'secret: {secrets}')

        except HTTPClientError as e:
            self.write(f'HTTPError: Status {e.code} <br> URL: {url} <br> {str(e.response.body)} <br> Done')
            self.finish()
            return
        
        # We will be using the base32 encoded secret as it has to be used in a authenticator app. eg. Google Authenticator.
        secret = secrets['secretBase32Encoded']   
        username = self.current_user['user']['username']
        application = 'companyX'

        # Format : otpauth://TYPE/LABEL?PARAMETERS | Example: otpauth://totp/Example:alice@google.com?secret=JBSWY3DPEHPK3PXP&issuer=Example
        # Refer https://github.com/google/google-authenticator/wiki/Key-Uri-Format
        totp_URI = f'otpauth://totp/{application}:{username}?secret={secret}&issuer={application}'
        
        # Encode TOTP-URI in a QR Code
        QR_img = qrcode.make(totp_URI)
        path = '/static/qrcodes/{secret}.png' # Path used to serve the QR Code
        abs_path = BASE_DIR + path # Path of the QR Code in the filesystem

        # Save the QR code
        QR_img.save(abs_path)
        
        # Display QR Code
        self.write(f'''
            <img src={path} alt='cannot load'></img>
            <br>
            Base32 Secret: {secret}
            <br>

            <form method="POST" action="/enableMFA">
                <input type="text" name="code" placeholder="Enter the code here"></input>
                <input type="hidden" name="secretBase32" value="{secret}"></input>

                <input type="submit">
            </form>
        ''')


    async def post(self):
        access_token = self.get_secure_cookie('access_token').decode('UTF-8')

        code = self.get_body_argument("code") # TOTP App generated code
        secret = self.get_body_argument("secretBase32") # Secret Genearated by Fusionauth

        path = '/static/qrcodes/{secret}.png'
        abs_path = BASE_DIR + path

        # Delete the QR CODE image
        os.remove(abs_path)


        url = 'http://localhost:9011/api/user/two-factor'
        # Body of the request
        data = {
            "code": code,
            "method": "authenticator",
            "secretBase32Encoded": secret,
        }
        data = escape.json_encode(data)

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = await http.fetch(
                url,
                body=data,
                method="POST",
                headers=headers,
            )
            response_data = escape.json_decode(response.body)
            recovery_codes = escape.json_encode(response_data['recoveryCodes']) # Convert Array to string

            self.write(f'''
                Your recovery codes are : {recovery_codes}

                <br><br>

                <a href="/"> Home </a>
            ''')

        except HTTPClientError as e:
            self.write(f'HTTPError: Status {e.code} <br> URL: {url} <br>')
            self.write(str(e.response.body))
            self.write(f' <br> Request Body: {data}')
        

# Incomplete Part 
# Please ignore this class!
# Purpose: Let admin enable MFA to users
class AdminEnableMFA(BaseHandler):
    allowed_roles = ['superadmin', 'admin']
    @tornado.web.authenticated
    async def get(self):
        if self.current_user['user']['registrations'][0]['roles'][0] in self.allowed_roles:
            query = {
              "bool" : {
                "must" : [ [ {
                  "nested" : {
                    "path" : "registrations",
                    "query" : {
                      "bool" : {
                        "must" : [ {
                          "match" : {
                            "registrations.applicationId" : "565e1d30-1d51-4f04-8e21-52c9353da83f"
                          }
                        } ]
                      }
                    }
                  }
                } ] ]
              }
            }
            body = {
                "search": {
                    "queryString": "*",
                    "sortFields": [
                        {
                            "name": "username",
                            "order": "asc"
                        }
                    ],
                    "startRow": 0
                }
            }         

            body = escape.json_encode(body)
            print(body)

            query = urllib.parse.urlencode(query)
            
            url = f'http://localhost:9011/api/user/search'

            headers = {
                'Authorization': f'{api_key}',
                'Content-Type': 'application/json'
            }
            
            try:
                response = await http.fetch(
                    url,
                    method='POST',
                    body=body,
                    headers=headers,
                )
                self.write(escape.json_decode(response.body))

            except HTTPClientError as e:
                self.write(f'Unauthorized else: Status {e.code} <br>')
                self.write(str(e.response.body))
                

            self.write('<br>You are allowed')
        else:
            self.write('you are not allowed')

# Disable 2FA for a user
class DisableMFAHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        # Get two factor Method ID
        method = self.current_user['user']['twoFactor'].get('methods')

        # If twofactor is not enabled
        if not(method):
            self.write("You have not enabled MFA <br> <a href='/'>Home</a>")
            return

        self.write('''
            <form method="POST" action="/disableMFA">
                <input type="text" name="code" placeholder="Enter Code here">
                <input type="submit">
            </form>
        ''')

    async def post(self):
        access_token = self.get_secure_cookie("access_token").decode("UTF-8")
        code = self.get_body_argument("code")
        methodid = self.current_user['user']['twoFactor']['methods'][0]['id']

        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        
        query = {
            'code': code,
            'methodId': methodid
        }
        query = urllib.parse.urlencode(query)

        url = f'http://localhost:9011/api/user/two-factor?{query}'

        try:
            response = await http.fetch(
                url,
                method="DELETE",
                headers=headers,
            )
            self.write(f'''
                <div>Successfully disabled MFA</div>
                <br>

                <a href="/"> Home </a>
            ''')

        except HTTPClientError as e:
            if e.code == 421:
                self.write("Invalid Code Please try again. <br>")
                self.write("<a href='/disableMFA'>Try again</a>")
                return

            self.write(f'HTTPError: Status {e.code} <br> URL: {url} <br>')
            self.write(str(e.response.body))
