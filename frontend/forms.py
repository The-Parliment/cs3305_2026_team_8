from wtforms import BooleanField, DateTimeLocalField, Form, StringField, PasswordField, SubmitField, DateTimeField, FloatField
from wtforms.validators import DataRequired, Length, InputRequired
import datetime
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
    
class EventForm(Form):
    title = StringField("Event Title", validators=[Length(min=2, max=64)])
    venue = StringField("Event Venue", validators=[Length(min=2, max=128)])   
    datetime_start = DateTimeLocalField("Start Time", format=['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S'], validators=[InputRequired()])
    datetime_end = DateTimeLocalField("End Time", format=['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S'], validators=[InputRequired()])
    latitude = FloatField("Latitude")
    longitude = FloatField("Longitude")
    description = StringField("Event Description", validators=[Length(min=2, max=256)])
    is_public = BooleanField("Public Event", default=True)
    submit = SubmitField("Submit")
