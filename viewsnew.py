# todo main pages like pics music est. as well as random pages in a map site. like going into a rabithole.




import os
from _socket import gethostname

from flask import Flask, render_template_string, render_template, request, flash
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
from flask.ext.login import current_user

app = Flask(__name__)


# Use a Class-based config to avoid needing a 2nd file
# os.getenv() enables configuration through OS environment variables
class ConfigClass(object):
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'THIS IS AN INSECURE SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///basic_app.sqlite')
    CSRF_ENABLED = True

    # Flask-Mail settings
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'spoontheprune@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', )
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '"Spoon The Prune" <noreply@example.com>')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_SSL = int(os.getenv('MAIL_USE_SSL', False))
    MAIL_USE_TLS = int(os.getenv('MAIL_USE_TLS', True))
    # Flask-User settings
    USER_APP_NAME = "Spoon The Prune"  # Used by email templates


def create_app():
    """ Flask application factory """

    # Setup Flask app and app.config
    # app = Flask(__name__)
    app.config.from_object(__name__ + '.ConfigClass')

    # Initialize Flask extensions
    db = SQLAlchemy(app)  # Initialize Flask-SQLAlchemy
    mail = Mail(app)  # Initialize Flask-Mail

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
    db_adapter = SQLAlchemyAdapter(db, User)  # Register the User model
    user_manager = UserManager(db_adapter, app)  # Initialize Flask-User

    # The Home page is accessible to anyone
    @app.route('/home')
    def home_page():
        return render_template('home.html', title='Home')

    @app.route('/')
    def startup():
        return render_template('startup_page_new.html')

    # videos

    @app.route('/videos')
    def videos():
        return render_template('videos.html', title='videos')

    @app.route('/videos/fast')
    def videos_fast():
        return render_template('video_base.html', video_title='FAST', video='https://www.youtube.com/embed/E_ueE1kaUHI',
                               description='A story of a boy and his relentless and sometimes tragic dream. A dream of speed. A dream of FAST.')

    @app.route('/videos/sik-points')
    @login_required
    def videos_sikPoints():
        return render_template('sikpoints.html')

    @app.route('/videos/test')
    def videos_test():
        return render_template('video_base.html', video_title='Test', video='/static/videos/test.mp4',
                               description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus convallis odio id mauris scelerisque, at pharetra tellus lobortis. Proin at diam eget est imperdiet pellentesque at ut elit. Aliquam vulputate sem eu tellus dignissim, sit amet tincidunt lorem ornare. Integer lacinia ligula ac tristique pellentesque. Integer tortor nisi, sollicitudin id sodales a, bibendum eget tellus. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Suspendisse potenti. Praesent id nulla feugiat, eleifend felis ac, placerat arcu. Curabitur vitae consequat neque. Sed malesuada odio sit amet egestas laoreet. Proin vel sollicitudin enim. Nam blandit sed eros et pretium. Etiam at aliquam nunc. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.Pellentesque sem dolor, pulvinar imperdiet quam malesuada, faucibus tempor velit. Mauris metus odio, eleifend et eros et, eleifend sagittis enim. Cras semper risus ac lorem convallis, nec hendrerit eros vestibulum. Sed eget erat a erat dictum commodo. Vestibulum ac accumsan odio. Nunc scelerisque tortor turpis. Duis sodales fringilla finibus. Vivamus convallis convallis dolor non ultricies. Ut porttitor vehicula leo quis sodales. Pellentesque convallis ullamcorper rhoncus. Vivamus sed quam vel massa malesuada consectetur. Morbi porta lacus et velit laoreet egestas. Curabitur vehicula odio a congue rhoncus.')

    @app.route('/videos/equation')
    def videos_equation():
        return render_template('videoEquation.html')

    # flamenco

    @app.route('/flamenco')
    def flamenco():
        return render_template('')

    # music


    @app.route('/music')
    def music():
        return render_template('music.html', title='Sounds')

    # pictures

    @app.route('/pictures')
    def pictures():
        return render_template('pictures.html', title='Pictures')

    # words

    @app.route('/words')
    def words():
        return render_template('words.html', title='Words')


    @app.route('/contact', methods=['POST', 'GET'])


    @login_required
    def contact():
        if request.method == 'POST':
            message = request.form['Message']

            with open(Flask(__name__).root_path + '/Message.txt', mode='a', encoding='utf-8') as a_file:
                a_file.write(message + ":" + current_user.username  + "\n")
            flash("Thanks for the message. Im sure it was great + I will read it at some point. ", category='info')

        return render_template("contact.html")


    @app.route('/prune')
    def prune_spin():
        return render_template('prune_spin.html')
    # The Members page is only accessible to authenticated users


    return app

create_app()

# Start development web server
if __name__ == '__main__':
    if 'liveconsole' not in gethostname():
        app.run()
