import os

from flask import Flask, render_template, request, flash, redirect, session, g, url_for
# from fromflask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
# from werkzeug.datastructures import MultiDict
# from wtforms import Form
# from wtforms_sqlalchemy.orm import model_form
from flask_wtf.csrf import CSRFProtect

from forms import UserAddForm, LoginForm, MessageForm, UserProfileForm
from models import db, connect_db, User, Message
from decorators import authenticated

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config.from_object('config.ConfigDev')

# # Get DB_URI from environ variable (useful for production/testing) or,
# # if not set there, use development local db.
# app.config['SQLALCHEMY_DATABASE_URI'] = (
#     # os.environ.get('DATABASE_URL', 'jdbc:mysql://localhost:3306/unit_26'))
#     os.environ.get('DATABASE_URL', 'mysql+pymysql://acampos:root@localhost:3306/unit_26'))
#
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = False
# # app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# # toolbar = DebugToolbarExtension(app)
csrf = CSRFProtect()
csrf.init_app(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])  # Almir: this stores a full 'user object' into the globals

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    # IMPLEMENT THIS
    session.pop(CURR_USER_KEY)
    flash('User logged out', category='success')
    return redirect(url_for('login'))


######################################################################
# General user routes:

######################################################################
# General user routes:

######################################################################
# General user routes:
######################################################################
#                                                           LIST USERS
@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


######################################################################
#                                                            SHOW USER
@app.route('/users/<int:user_id>')
@authenticated
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())
    return render_template('users/show.html', user=user, messages=messages)


######################################################################
#                                                            FOLLOWING
@app.route('/users/<int:user_id>/following')
@authenticated
def show_following(user_id):
    """Show list of people this user is following."""

    # if not g.user:
    #     flash("Access unauthorized.", "danger")
    #     return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


######################################################################
#                                                            FOLLOWERS
@app.route('/users/<int:user_id>/followers')
@authenticated
def users_followers(user_id):
    """Show list of followers of this user."""

    # if not g.user:
    #     flash("Access unauthorized.", "danger")
    #     return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


######################################################################
#                                                               FOLLOW
@app.route('/users/follow/<int:follow_id>', methods=['POST'])
@authenticated
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    # if not g.user:
    #     flash("Access unauthorized.", "danger")
    #     return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


######################################################################
#                                                       STOP FOLLOWING
@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
@authenticated
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


######################################################################
#                                                                 EDIT
@app.route('/users/profile', methods=["GET", "POST"])
@authenticated
def profile():
    """Update profile for current user."""
    form = UserProfileForm(obj=g.user)
    if request.method == 'GET':
        return render_template('users/edit.html',
                               form=form)
    else:
        if form.validate_on_submit():
            if User.authenticate(g.user.username, form.password.data):
                user = User.query.get_or_404(g.user.id)
                pwd = user.password
                form.populate_obj(user)
                user.password = pwd
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('users_show', user_id=user.id))
            flash(u'Invalid Password', category='danger')
            return render_template('users/edit.html',
                                   form=form)
        else:
            flash(u'Validation Problem', category='danger')
            return render_template('users/edit.html',
                                   form=form)

# ######################################################################
# #                                                                 EDIT
# @app.route('/users/profile', methods=["GET", "POST"])
# @authenticated
# def profile():
#     """Update profile for current user."""
#     UPF = model_form(User, db.session,
#                      exclude=['messages', 'followers', 'following', 'likes'])
#     # UPF=model_form(User, db.session)
#     if request.method == 'GET':
#         form = UPF(MultiDict(), g.user)
#         form.password.data = ''
#         return render_template('users/edit.html',
#                                form=form)
#     else:
#         form = UPF(request.form, obj=g.user)
#         if form.validate():
#             if User.authenticate(g.user.username, form.password.data):
#                 user = User.query.get_or_404(g.user.id)
#                 pwd = user.password
#                 form.populate_obj(user)
#                 user.password = pwd
#                 db.session.add(user)
#                 db.session.commit()
#                 return redirect(url_for('users_show', user_id=user.id))
#             flash(u'Invalid Password', category='danger')
#             return render_template('users/edit.html',
#                                    form=form)
#         else:
#             flash(u'Validation Problem', category='danger')
#             return render_template('users/edit.html',
#                                    form=form)
#

######################################################################
#                                                               DELETE
@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


######################################################################
# Messages routes:
######################################################################
# Messages routes:
######################################################################
# Messages routes:
######################################################################
#                                                                  NEW
@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get(message_id)
    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    if g.user:
        messages = (Message
                    .query
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())

        return render_template('home.html', messages=messages)

    else:
        return render_template('home-anon.html')


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req


if __name__ == '__main__':
    app.run()
