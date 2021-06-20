import tornado.ioloop
import tornado.web

from controllers.auth import *
from controllers.home import *
from controllers.rolePermissions import *
from controllers.MFAController import *

import settings

def make_app():
    return tornado.web.Application(
        [
            (r"/", HomeController),
            (r"/login", FushionAuthLoginController),
            (r"/callback", FushionAuthLoginController),
            (r"/logout", LogoutController),

            # 2FA 
            (r"/enableMFA", EnableMFA),
            (r"/disableMFA", DisableMFAHandler),

            # Static file Handler to serve QR Code Images
            (r"/static/qrcodes/(.*)", tornado.web.StaticFileHandler, {"path": settings.BASE_DIR + '/static/qrcodes'})
        ],
        **settings.app_settings
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()

