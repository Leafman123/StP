# todo main pages like pics music est. as well as random pages in a map site. like going into a rabithole.
import datetime
import json
import os
from _socket import gethostname

import flask_user
import requests
from flask import Flask, render_template_string, render_template, request, flash, current_app, url_for, redirect
from flask.ext.mobility.decorators import mobile_template
from flask_mobility import Mobility
from flask.ext.user.views import _send_registered_email, _endpoint_url, _do_login_user
from flask_mail import Mail, signals
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
from flask.ext.login import current_user


app = Flask(__name__)
Mobility(app)

# Use a Class-based config to avoid needing a 2nd file
# os.getenv() enables configuration through OS environment variables
class ConfigClass(object):
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'THIS IS AN INSECURE SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATAfBASE_URL', 'sqlite:///basic_app.sqlite')
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


def captcha_test(request):
    payload = {'secret': os.getenv('CAPTCHA_SECRET'), 'response': request.values['g-recaptcha-response'] }
    g_result = requests.post('https://www.google.com/recaptcha/api/siteverify', payload )
    return json.loads(g_result.text)["success"]


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

    def my_register():

        user_manager = current_app.user_manager
        db_adapter = user_manager.db_adapter

        next = request.args.get('next', _endpoint_url(user_manager.after_login_endpoint))
        reg_next = request.args.get('reg_next', _endpoint_url(user_manager.after_register_endpoint))

        # Initialize form
        login_form = user_manager.login_form()  # for login_or_register.html
        register_form = user_manager.register_form(request.form)  # for register.html

        # invite token used to determine validity of registeree
        invite_token = request.values.get("token")

        # require invite without a token should disallow the user from registering
        if user_manager.require_invitation and not invite_token:
            flash("Registration is invite only", "error")
            return redirect(url_for('user.login'))

        user_invite = None
        if invite_token and db_adapter.UserInvitationClass:
            user_invite = db_adapter.find_first_object(db_adapter.UserInvitationClass, token=invite_token)
            if user_invite:
                register_form.invite_token.data = invite_token
            else:
                flash("Invalid invitation token", "error")
                return redirect(url_for('user.login'))

        if request.method != 'POST':
            login_form.next.data = register_form.next.data = next
            login_form.reg_next.data = register_form.reg_next.data = reg_next
            if user_invite:
                register_form.email.data = user_invite.email



        # Process valid POST
        if request.method == 'POST' and captcha_test(request) and register_form.validate():
            # Create a User object using Form fields that have a corresponding User field
            User = db_adapter.UserClass
            user_class_fields = User.__dict__
            user_fields = {}

            # Create a UserEmail object using Form fields that have a corresponding UserEmail field
            if db_adapter.UserEmailClass:
                UserEmail = db_adapter.UserEmailClass
                user_email_class_fields = UserEmail.__dict__
                user_email_fields = {}

            # Create a UserAuth object using Form fields that have a corresponding UserAuth field
            if db_adapter.UserAuthClass:
                UserAuth = db_adapter.UserAuthClass
                user_auth_class_fields = UserAuth.__dict__
                user_auth_fields = {}

            # Enable user account
            if db_adapter.UserProfileClass:
                if hasattr(db_adapter.UserProfileClass, 'active'):
                    user_auth_fields['active'] = True
                elif hasattr(db_adapter.UserProfileClass, 'is_enabled'):
                    user_auth_fields['is_enabled'] = True
                else:
                    user_auth_fields['is_active'] = True
            else:
                if hasattr(db_adapter.UserClass, 'active'):
                    user_fields['active'] = True
                elif hasattr(db_adapter.UserClass, 'is_enabled'):
                    user_fields['is_enabled'] = True
                else:
                    user_fields['is_active'] = True

            # For all form fields
            for field_name, field_value in register_form.data.items():
                # Hash password field
                if field_name == 'password':
                    hashed_password = user_manager.hash_password(field_value)
                    if db_adapter.UserAuthClass:
                        user_auth_fields['password'] = hashed_password
                    else:
                        user_fields['password'] = hashed_password
                # Store corresponding Form fields into the User object and/or UserProfile object
                else:
                    if field_name in user_class_fields:
                        user_fields[field_name] = field_value
                    if db_adapter.UserEmailClass:
                        if field_name in user_email_class_fields:
                            user_email_fields[field_name] = field_value
                    if db_adapter.UserAuthClass:
                        if field_name in user_auth_class_fields:
                            user_auth_fields[field_name] = field_value

            # Add User record using named arguments 'user_fields'
            user = db_adapter.add_object(User, **user_fields)
            if db_adapter.UserProfileClass:
                user_profile = user

            # Add UserEmail record using named arguments 'user_email_fields'
            if db_adapter.UserEmailClass:
                user_email = db_adapter.add_object(UserEmail,
                                                   user=user,
                                                   is_primary=True,
                                                   **user_email_fields)
            else:
                user_email = None

            # Add UserAuth record using named arguments 'user_auth_fields'
            if db_adapter.UserAuthClass:
                user_auth = db_adapter.add_object(UserAuth, **user_auth_fields)
                if db_adapter.UserProfileClass:
                    user = user_auth
                else:
                    user.user_auth = user_auth

            require_email_confirmation = True
            if user_invite:
                if user_invite.email == register_form.email.data:
                    require_email_confirmation = False
                    db_adapter.update_object(user, confirmed_at=datetime.utcnow())

            db_adapter.commit()

            # Send 'registered' email and delete new User object if send fails
            if user_manager.send_registered_email:
                try:
                    # Send 'registered' email
                    _send_registered_email(user, user_email, require_email_confirmation)
                except Exception as e:
                    # delete new User object if send  fails
                    db_adapter.delete_object(user)
                    db_adapter.commit()
                    raise

            # Send user_registered signal
            flask_user.signals.user_registered.send(current_app._get_current_object(),
                                         user=user,
                                         user_invite=user_invite)

            # Redirect if USER_ENABLE_CONFIRM_EMAIL is set
            if user_manager.enable_confirm_email and require_email_confirmation:
                next = request.args.get('next', _endpoint_url(user_manager.after_register_endpoint))
                return redirect(next)

            # Auto-login after register or redirect to login page
            next = request.args.get('next', _endpoint_url(user_manager.after_confirm_endpoint))
            if user_manager.auto_login_after_register:
                return _do_login_user(user, reg_next)  # auto-login
            else:
                return redirect(url_for('user.login') + '?next=' + reg_next)  # redirect to login page

        # Process GET or invalid POST
        return render_template(user_manager.register_template,
                               form=register_form,
                               login_form=login_form,
                               register_form=register_form)

    # Setup Flask-User
    db_adapter = SQLAlchemyAdapter(db, User)  # Register the User model
    user_manager = UserManager(db_adapter, app,
                               register_view_function= my_register)  # Initialize Flask-User

    # View functions
    # user_manager.init_app(app)

    # The Home page is accessible to anyone
    @app.route('/home')
    def home_page():
        return render_template('home.html', title='Home')


    @app.route('/')
    @mobile_template('{mobile/}startup_page.html')
    def startup(template):
        return render_template(template)

    #wormhole
    @app.route('/worm')
    def wormhole():
        return render_template('worm1.html', title='Wormhole')

    # videos

    @app.route('/videos')
    def videos():
        return render_template('videos/videos.html', title='videos')

    @app.route('/videos/fast')
    def videos_fast():
        return render_template('videos/video_base.html', title='Fast', video_title='FAST',
                               video='https://www.youtube.com/embed/E_ueE1kaUHI',
                               description='A story of a boy and his relentless and sometimes tragic dream. A dream of speed. A dream of FAST.')

    @app.route('/videos/trance')
    def videos_trance():
        return render_template('videos/video_base.html', title='Trance', video_title='Trance',
                               video='https://www.youtube.com/embed/y2QrxXwcvBU?rel=0&amp;controls=0',
                               description="and that's how my house burnt down.")


    @app.route('/videos/sik-points')
    @login_required
    def videos_sikPoints():
        return render_template('videos/sikpoints.html')

    @app.route('/videos/test')
    def videos_test():
        return render_template('videos/video_base.html', video_title='Test', video='/static/videos/test.mp4',
                               description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus convallis odio id mauris scelerisque, at pharetra tellus lobortis. Proin at diam eget est imperdiet pellentesque at ut elit. Aliquam vulputate sem eu tellus dignissim, sit amet tincidunt lorem ornare. Integer lacinia ligula ac tristique pellentesque. Integer tortor nisi, sollicitudin id sodales a, bibendum eget tellus. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Suspendisse potenti. Praesent id nulla feugiat, eleifend felis ac, placerat arcu. Curabitur vitae consequat neque. Sed malesuada odio sit amet egestas laoreet. Proin vel sollicitudin enim. Nam blandit sed eros et pretium. Etiam at aliquam nunc. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.Pellentesque sem dolor, pulvinar imperdiet quam malesuada, faucibus tempor velit. Mauris metus odio, eleifend et eros et, eleifend sagittis enim. Cras semper risus ac lorem convallis, nec hendrerit eros vestibulum. Sed eget erat a erat dictum commodo. Vestibulum ac accumsan odio. Nunc scelerisque tortor turpis. Duis sodales fringilla finibus. Vivamus convallis convallis dolor non ultricies. Ut porttitor vehicula leo quis sodales. Pellentesque convallis ullamcorper rhoncus. Vivamus sed quam vel massa malesuada consectetur. Morbi porta lacus et velit laoreet egestas. Curabitur vehicula odio a congue rhoncus.')

    @app.route('/videos/ben-beat')
    def videos_ben_beat ():
        return render_template('videos/video_base.html', video_title='Ben Beat', video='https://www.youtube.com/embed/FWriisbCKkg',
                               description='PURE FIRE')


    @app.route('/videos/equation')
    def videos_equation():
        return render_template('videos/videoEquation.html')

    # music

    @app.route('/music')
    def music():
        return render_template('music.html', title='Sounds')

    # pictures

    @app.route('/pictures')
    def pictures():
        return render_template('pictures/pictures.html', title='Pictures')

    @app.route('/flamenco')
    def flamenco():
        return render_template('pictures/flamenco.html', title="Flamenco")


    @app.route('/pictures/school')
    def schoolpic():
        return render_template('pictures/school_pictures.html', title="Paint school")

    @app.route('/pictures/hateyhate')
    def hateyhate():
        return render_template('pictures/sam_edge.html',title = "TooEdge5Me")

    @app.route('/pictures/fen')
    def fenbish():
        return render_template('pictures/fen.html',title = "TooEdge5Me")

    # words

    @app.route('/words')
    def words():
        return render_template('words/words.html', title='Words')

    @app.route('/words/guides')
    def words_guides():
        return render_template('words/guides.html', title='Guides')

    @app.route('/contact', methods=['POST', 'GET'])
    @login_required
    def contact():
        if request.method == 'POST':
            message = request.form['Message']

            with open(Flask(__name__).root_path + '/Message.txt', mode='a', encoding='utf-8') as a_file:
                a_file.write(message + ":" + current_user.username + "\n")
            flash("Thanks for the message. Im sure it was great + I will read it at some point. ", category='info')

        return render_template("contact.html", title='contact')

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
