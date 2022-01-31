
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_admin import Admin
from flask_talisman import Talisman

app = Flask(__name__)

limiter = Limiter(app, key_func=get_remote_address)
limiter.init_app(app)
csp = {
    'default-src': ['\'self\'',
                    '*.cloudflare.com',
                    '*.googleapis.com'],
    'frame-ancestors': '\'self\'',
    'form-action': '\'self\''
}
Talisman(app, content_security_policy=csp, force_https=False, session_cookie_secure=False)
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

app.config.update(dict(
    DEBUG = False,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'flaskassignmenttest1@gmail.com',
    MAIL_PASSWORD = 'MyDummyAccount1',
))
mail = Mail(app)
csrf = CSRFProtect(app)
csrf.init_app(app)
app.config['SECRET_KEY'] = 'f31dbde16a08b1eaefe6849975e5a64d0c8964f364b41a6c'
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://c1422379:kXMhK9qgZzuike8@csmysql.cs.cf.ac.uk:3306/c1422379_blog'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

flask_admin = Admin(app, name='microblog', template_mode='bootstrap3')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from blog import routes