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