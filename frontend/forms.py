from wtforms import Form, StringField, PasswordField, SubmitField, DateTimeField, FloatField
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
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    email = StringField("Email", validators=[Length(min=2, max=128)])
    phone_number = StringField("Phone Number", validators=[Length(min=10, max=15)])
    submit = SubmitField("Submit")

class EditEventForm(Form):
    title = StringField("Event Title", validators=[Length(min=2, max=64)])
    venue = StringField("Event Venue", validators=[Length(min=2, max=128)])   
    datetime_start = DateTimeField("Start Time", format="%Y-%m-%dT%H:%M")
    datetime_end = DateTimeField("End Time", format="%Y-%m-%dT%H:%M")
    latitude = FloatField("Latitude")
    longitude = FloatField("Longitude")
    description = StringField("Event Description", validators=[Length(min=2, max=256)])
    submit = SubmitField("Submit")
