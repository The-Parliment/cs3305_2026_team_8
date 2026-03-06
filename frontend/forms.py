from wtforms import BooleanField, DateTimeLocalField, Form, StringField, PasswordField, SubmitField, DateTimeField, FloatField, TextAreaField, IntegerRangeField
from wtforms.validators import DataRequired, Length, InputRequired
from wtforms.widgets import HiddenInput
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
    title = TextAreaField("Event Title", validators=[Length(min=2, max=64)])
    description = TextAreaField("Event Description", validators=[Length(min=2)])
    datetime_start = DateTimeLocalField("Start Time", format=['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S'], validators=[InputRequired()])
    datetime_end = DateTimeLocalField("End Time", format=['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S'], validators=[InputRequired()])
    latitude = FloatField("Latitude", widget=HiddenInput())
    longitude = FloatField("Longitude", widget=HiddenInput())
    is_public = BooleanField("Public Event", default=True)
    submit = SubmitField("Submit")

class GroupForm(Form):
    group_name = TextAreaField("Group Name", validators=[Length(min=2, max=64), DataRequired()])
    group_desc = TextAreaField("Group Description", validators=[Length(min=2, max=256), DataRequired()])
    is_public = BooleanField("Public Group", default=True)
    submit = SubmitField("Submit")
    
class CommunityForm(Form):
    user = StringField("Username")
    submit = SubmitField("Submit")
    
class SearchEventForm(Form):
    title = StringField("Title")
    host = StringField("Host")
    datetime_start = DateTimeLocalField("Start Time", format=['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S'])
    datetime_end = DateTimeLocalField("End Time", format=['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S'])
    latitude = FloatField("Latitude")
    longitude = FloatField("Longitude")
    radius = IntegerRangeField("Area", default=5)
    submit = SubmitField("Search")
