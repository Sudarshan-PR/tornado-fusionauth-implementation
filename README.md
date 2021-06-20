## Fusionauth Authentication in Tornado
- - -

This a sample backend written in python (Tornado Framework) which will be using Fusionauth to handle authentication.


Before starting make sure you have [setup fusionauth](https://fusionauth.io/docs/v1/tech/installation-guide/fusionauth-app/).
This code assumes you have Fusionauth runnning on `localhost` and is listening to port `9011`.
- - -

#### Features included:
Fusionauth Related:
* Login (Access Token)
* Logout
* Retrieve Userinfo
* 2 Factor Authentication Using Authenticators.
* Groups

Application Related:
* Authorization (Using pycasbin)
- - -

#### Environment Variables To Be Set:
Below values must be include in a `.env` file in the projects root directory. <small>(i.e same folder as `main.py`)</small>
* FUSIONAUTH_KEY
* FUSIONAUTH_SECRET_KEY
* FUSIONAUTH_MGMT_KEY
* FUSIONAUTH_CLIENT_ID
* COOKIE_SECRET

- - -
#### Run the server:
    $ pip install -r requirements.txt

    $ python main.py