import tornado.web
from controllers.RequestHandler import BaseHandler

# Home screen
class HomeController(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        groups = await self.get_group_details()

        self.write(f'''
            <h1> Welcome {self.current_user['user']['registrations'][0]['username']} </h1> 
            <br>

            <div>
                Current User: {self.current_user}
            </div>
            <br>

            <div>
                Groups: {groups}
            </div>
            <br>

            <div>
                Permissions: {self.user_permissions}
            </div>
            <br>

            <div>
                <a href="/enableMFA"> Enable 2FA </a> <br>
                <a href="/disableMFA"> Disable 2FA </a> <br>
            </div>
            <br>

            <a href='/logout'> Logout </a>
            '''
        )
