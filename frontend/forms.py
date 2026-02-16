from wtforms import Form, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, InputRequired

class LoginForm(Form):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=32)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4, max=64)])
    submit = SubmitField("Submit")

class RegisterForm(Form):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=32)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField("Email", validators=[DataRequired(), Length(min=2, max=128)])
    phone_number = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField("Submit")
    
class ChangeDetailsForm(Form):
    new_username = StringField("Username")
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    email = StringField("Email", validators=[Length(min=2, max=128)])
    phone_number = StringField("Phone Number", validators=[Length(min=10, max=15)])
    submit = SubmitField("Submit")

class ChangePasswordForm(Form):
    old_password = PasswordField("Old Password", validators=[DataRequired(), Length(min=4, max=64)])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=4, max=64)])
    submit = SubmitField("Submit")