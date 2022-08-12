from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, URL, Optional


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


class UpdateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL', 
                            validators=[URL(),Optional()])
    header_image_url = StringField('(Optional) Image URL', 
                            validators=[URL(),Optional()])
    bio = TextAreaField('(Optional)')
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class CSRFProtectionForm(FlaskForm):
    """For actions where we want CSRF protection, but don't need any fields.

    Currently used for our "delete" buttons, which make POST requests, and the
    logout button, which makes POST requests.
    """
