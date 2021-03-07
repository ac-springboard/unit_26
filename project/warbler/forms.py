from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Length


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


# class UserProfileForm(ModelForm):
#     class Meta:
#         model = User
#     email = EmailField('Email Address', validators=[DataRequired(), Email()])

class UserProfileForm(FlaskForm):
    id = HiddenField()
    email = StringField('Email', [Email(message=('Invalid email address.')), DataRequired(message=('Email address is required.'))])
    username = StringField('Username', [DataRequired(message=('Username is required.'))])
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Header Image URL')
    bio = StringField('(Optional) Header Image URL')
    password = PasswordField('Password', [DataRequired(message=('Password is required.'))])
    submit = SubmitField('Submit')
