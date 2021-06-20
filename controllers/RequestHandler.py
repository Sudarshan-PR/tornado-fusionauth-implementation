import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPClientError

from tornado import escape

http = AsyncHTTPClient()

# Base Handler for auth purpose
class BaseHandler(tornado.web.RequestHandler):
    '''
    prepare() method is overloaded instead of get_current_user() as http call is to made in our usecase.
    
    Refer prepare() from https://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler.current_user
    '''
    async def prepare(self):
        access_token = self.get_secure_cookie("access_token")

        if access_token:
            access_token = access_token.decode('UTF-8')
            
            headers = {
                'Authorization': f'Bearer {access_token}'
            }

            try:
                response = await http.fetch(
                    "http://localhost:9011/api/user",
                    headers=headers
                )
                self.current_user = escape.json_decode(response.body)

            except HTTPClientError as e:
                self.redirect('/logout')


    async def get_group_details(self):
        api_key = 'IjjZlYsoMUTIXk5S3ElYXBipqjTAZpBdTw5X_9dyYXweP9gRSPASmwkj'
        groupId = self.current_user['user']['memberships'][0]['groupId']

        url = f'http://localhost:9011/api/group/{groupId}'

        headers = {
            'Authorization': f'{api_key}'
        }
        
        try:
            response = await http.fetch(
                url,
                headers=headers
            )
            return escape.json_decode(response.body)

        except HTTPClientError as e:
            return f'Unauthorized else: Status {e.code}'

    @property
    def user_permissions(self):
        perms = self.get_secure_cookie('permissions').decode('UTF-8')
        return escape.json_encode(perms)
