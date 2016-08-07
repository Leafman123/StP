#todo main pages like pics music est. as well as random pages in a map site. like going into a rabithole.




import os
from _socket import gethostname

from flask import Flask, render_template_string, render_template
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter

app = Flask(__name__)
# Use a Class-based config to avoid needing a 2nd file
# os.getenv() enables configuration through OS environment variables
class ConfigClass(object):
    # Flask settings
    SECRET_KEY =              os.getenv('SECRET_KEY',       'THIS IS AN INSECURE SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',     'sqlite:///basic_app.sqlite')
    CSRF_ENABLED = True


    # Flask-Mail settings
    MAIL_USERNAME =           os.getenv('MAIL_USERNAME',        'spoontheprune@gmail.com')
    MAIL_PASSWORD =           os.getenv('MAIL_PASSWORD',        )
    MAIL_DEFAULT_SENDER =     os.getenv('MAIL_DEFAULT_SENDER',  '"MyApp" <noreply@example.com>')
    MAIL_SERVER =             os.getenv('MAIL_SERVER',          'smtp.gmail.com')
    MAIL_PORT =           int(os.getenv('MAIL_PORT',            '587'))
    MAIL_USE_SSL =        int(os.getenv('MAIL_USE_SSL',         False))
    MAIL_USE_TLS = int(os.getenv('MAIL_USE_TLS',         True))
    # Flask-User settings
    USER_APP_NAME        = "AppName"                # Used by email templates


def create_app():
    """ Flask application factory """

    # Setup Flask app and app.config
    # app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')

    # Initialize Flask extensions
    db = SQLAlchemy(app)                            # Initialize Flask-SQLAlchemy
    mail = Mail(app)                                # Initialize Flask-Mail

    # Define the User data model. Make sure to add flask.ext.user UserMixin !!!
    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)

        # User authentication information
        username = db.Column(db.String(50), nullable=False, unique=True)
        password = db.Column(db.String(255), nullable=False, server_default='')
        reset_password_token = db.Column(db.String(100), nullable=False, server_default='')

        # User email information
        email = db.Column(db.String(255), nullable=False, unique=True)
        confirmed_at = db.Column(db.DateTime())

        # User information
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
        first_name = db.Column(db.String(100), nullable=False, server_default='')
        last_name = db.Column(db.String(100), nullable=False, server_default='')
        points = db.column(db.Integer)

    # Create all database tables
    db.create_all()

    # Setup Flask-User
    db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
    user_manager = UserManager(db_adapter, app)     # Initialize Flask-User

    # The Home page is accessible to anyone
    @app.route('/home')
    def home_page():
        return render_template('home.html', title = 'Home')

    @app.route('/')
    def startup():
        return render_template('startup_page_new.html')

    #videos

    @app.route('/videos')
    def videos():
        return render_template('videos.html')

    #flamenco

    @app.route('/flamenco')
    def flamenco():
        return render_template('')

    #music


    @app.route('/music')
    def music():
        return render_template('')


    #pictures

    @app.route('/pictures')
    def pictures():
        return render_template('pictures.html')





    @app.route('/prune')
    def prune_spin():
        return render_template ('prune_spin.html')
        # The Members page is only accessible to authenticated users


    return app
create_app()

# Start development web server
if __name__=='__main__':
    if 'liveconsole' not in gethostname():
        app.run()