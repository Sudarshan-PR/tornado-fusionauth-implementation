import os
from dotenv import load_dotenv

load_dotenv()

app_settings = {
        "cookie_secret": os.getenv('COOKIE_SECRET'),
        "login_url": "/login",
        }

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

fusionauth_key = os.getenv('FUSIONAUTH_KEY')
fusionauth_secret_key = os.getenv('FUSIONAUTH_SECRET_KEY')
fusionauth_mgmt_key = os.getenv('FUSIONAUTH_MGMT_KEY')
fusionauth_client_id = os.getenv('FUSIONAUTH_CLIENT_ID')