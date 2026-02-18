from common.db.engine import engine
from common.db.base import Base
from common.db.structures.structures import Events, User, UserDetails, UserRequest, RequestTypes, Status
from passlib.context import CryptContext
from .db import get_db
import common.db.structures
import datetime

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    temp_remove_in_production()

def seed_cork_dummy_events():
    db = get_db()
    utc = datetime.timezone.utc
    base_date = datetime.datetime(2024, 3, 1, 12, 0, tzinfo=utc)

    events = [
        Events(
            title="Live Music on Oliver Plunkett Street",
            venue="Oliver Plunkett Street",
            host="cillian",
            latitude=51.8979,
            longitude=-8.4706,
            datetime_start=base_date,
            datetime_end=base_date + datetime.timedelta(hours=2),
            description="Afternoon live music session in the city centre."
        ),
        Events(
            title="Shandon Tower Tour",
            venue="St. Anne's Church, Shandon",
            host="joana",
            latitude=51.9010,
            longitude=-8.4767,
            datetime_start=base_date + datetime.timedelta(days=1),
            datetime_end=base_date + datetime.timedelta(days=1, hours=1),
            description="Guided tour of the historic Shandon Bells."
        ),
        Events(
            title="UCC Tech Meetup",
            venue="University College Cork",
            host="darren",
            latitude=51.8920,
            longitude=-8.4923,
            datetime_start=base_date + datetime.timedelta(days=2),
            datetime_end=base_date + datetime.timedelta(days=2, hours=3),
            description="Student tech talks and networking."
        ),
        Events(
            title="English Market Food Tasting",
            venue="English Market",
            host="foodwise",
            latitude=51.8975,
            longitude=-8.4756,
            datetime_start=base_date + datetime.timedelta(days=3),
            datetime_end=base_date + datetime.timedelta(days=3, hours=2),
            description="Local artisan food sampling event."
        ),
        Events(
            title="Blackrock Castle Astronomy Night",
            venue="Blackrock Castle",
            host="roisin",
            latitude=51.8991,
            longitude=-8.4023,
            datetime_start=base_date + datetime.timedelta(days=4),
            datetime_end=base_date + datetime.timedelta(days=4, hours=2),
            description="Stargazing and space science talks."
        ),
        Events(
            title="Fitzgerald Park Yoga",
            venue="Fitzgerald Park",
            host="joana",
            latitude=51.8938,
            longitude=-8.4894,
            datetime_start=base_date + datetime.timedelta(days=5),
            datetime_end=base_date + datetime.timedelta(days=5, hours=1),
            description="Outdoor yoga session by the Lee."
        ),
        Events(
            title="Mahon Point Business Expo",
            venue="Mahon Point",
            host="darren",
            latitude=51.8850,
            longitude=-8.4010,
            datetime_start=base_date + datetime.timedelta(days=6),
            datetime_end=base_date + datetime.timedelta(days=6, hours=4),
            description="Local business showcase and networking."
        ),
        Events(
            title="Douglas Community Fair",
            venue="Douglas Village",
            host="roisin",
            latitude=51.8770,
            longitude=-8.4350,
            datetime_start=base_date + datetime.timedelta(days=7),
            datetime_end=base_date + datetime.timedelta(days=7, hours=3),
            description="Family-friendly community fair."
        ),
        Events(
            title="Ballincollig Park Run",
            venue="Ballincollig Regional Park",
            host="cillian",
            latitude=51.8878,
            longitude=-8.5852,
            datetime_start=base_date + datetime.timedelta(days=8),
            datetime_end=base_date + datetime.timedelta(days=8, hours=2),
            description="5k community park run."
        ),
        Events(
            title="Glanmire Farmers Market",
            venue="Glanmire Community Hall",
            host="foodwise",
            latitude=51.9140,
            longitude=-8.3990,
            datetime_start=base_date + datetime.timedelta(days=9),
            datetime_end=base_date + datetime.timedelta(days=9, hours=3),
            description="Fresh local produce and crafts."
        ),
        Events(
            title="Cork Opera House Tour",
            venue="Cork Opera House",
            host="roisin",
            latitude=51.8996,
            longitude=-8.4702,
            datetime_start=base_date + datetime.timedelta(days=10),
            datetime_end=base_date + datetime.timedelta(days=10, hours=1),
            description="Behind-the-scenes theatre tour."
        ),
        Events(
            title="Pairc Ui Chaoimh Stadium Tour",
            venue="Pairc Ui Chaoimh",
            host="darren",
            latitude=51.8985,
            longitude=-8.4356,
            datetime_start=base_date + datetime.timedelta(days=11),
            datetime_end=base_date + datetime.timedelta(days=11, hours=2),
            description="Explore Cork's iconic GAA stadium."
        ),
        Events(
            title="Cobh Harbour Walk",
            venue="Cobh Promenade",
            host="joana",
            latitude=51.8490,
            longitude=-8.2940,
            datetime_start=base_date + datetime.timedelta(days=12),
            datetime_end=base_date + datetime.timedelta(days=12, hours=2),
            description="Scenic harbour walk and history talk."
        ),
        Events(
            title="Blarney Castle Visit",
            venue="Blarney Castle",
            host="cillian",
            latitude=51.9330,
            longitude=-8.5700,
            datetime_start=base_date + datetime.timedelta(days=13),
            datetime_end=base_date + datetime.timedelta(days=13, hours=3),
            description="Castle grounds exploration and tour."
        ),
        Events(
            title="Midleton Distillery Experience",
            venue="Midleton Distillery",
            host="foodwise",
            latitude=51.9156,
            longitude=-8.1750,
            datetime_start=base_date + datetime.timedelta(days=14),
            datetime_end=base_date + datetime.timedelta(days=14, hours=2),
            description="Guided tour and tasting experience."
        ),
        Events(
            title="Kinsale Coastal Walk",
            venue="Kinsale Harbour",
            host="roisin",
            latitude=51.7070,
            longitude=-8.5300,
            datetime_start=base_date + datetime.timedelta(days=15),
            datetime_end=base_date + datetime.timedelta(days=15, hours=2),
            description="Guided scenic coastal walk."
        ),
        Events(
            title="Carrigaline Community Meetup",
            venue="Carrigaline Court Hotel",
            host="darren",
            latitude=51.8120,
            longitude=-8.3980,
            datetime_start=base_date + datetime.timedelta(days=16),
            datetime_end=base_date + datetime.timedelta(days=16, hours=2),
            description="Local networking and community discussion."
        ),
        Events(
            title="Sunday Brunch Social",
            venue="City Centre Cafe",
            host="foodwise",
            latitude=51.8988,
            longitude=-8.4750,
            datetime_start=base_date + datetime.timedelta(days=17),
            datetime_end=base_date + datetime.timedelta(days=17, hours=2),
            description="Casual brunch and social gathering."
        ),
        Events(
            title="Lee Fields Football Match",
            venue="The Mardyke",
            host="cillian",
            latitude=51.8933,
            longitude=-8.4949,
            datetime_start=base_date + datetime.timedelta(days=18),
            datetime_end=base_date + datetime.timedelta(days=18, hours=2),
            description="Friendly five-a-side match."
        ),
        Events(
            title="Evening Poetry Reading",
            venue="Cork City Library",
            host="joana",
            latitude=51.8976,
            longitude=-8.4710,
            datetime_start=base_date + datetime.timedelta(days=19),
            datetime_end=base_date + datetime.timedelta(days=19, hours=1, minutes=30),
            description="Local poets share their latest work."
        ),
    ]
    db.add_all(events)
    db.commit()

def temp_remove_in_production():
    db = get_db()
    user1 = User(
        username="foodwise", hashed_password=pwd.hash("theclown")
    )
    user1_details = UserDetails(
        username="foodwise", first_name="Food", last_name="Wise", email="foodwise@example.com", phone_number="01234567890"
    )
    user2 = User(
        username="roisin", hashed_password=pwd.hash("quinn")
    )
    user2_details = UserDetails(
        username="roisin", first_name="Roisin", last_name="Quinn", email="roisin@example.com", phone_number="01234567891"
    )
    user3 = User(
        username="cillian", hashed_password=pwd.hash("oriain")
    )
    user3_details = UserDetails(
        username="cillian", first_name="Cillian", last_name="Oriain", email="cillian@example.com", phone_number="01234567892"
    )
    user4 = User(
        username="darren", hashed_password=pwd.hash("counihan")
    )
    user4_details = UserDetails(
        username="darren", first_name="Darren", last_name="Counihan", email="darren@example.com", phone_number="01234567893"
    )
    user5 = User(
        username="joana", hashed_password=pwd.hash("mafra")
    )
    user5_details = UserDetails(
        username="joana", first_name="Joana", last_name="Mafra", email="joana@example.com", phone_number="01234567894"
    )
    event = Events(
        id=1,
        title="Test Event",
        venue="Test Venue",
        host="cillian",
        latitude=53.3498,
        longitude=-6.2603,
        datetime_start=datetime.datetime(2024, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
        datetime_end=datetime.datetime(2024, 1, 1, 1, 0, tzinfo=datetime.timezone.utc),
        description="This is a test event."
    )
    req1 = UserRequest(
        field1="cillian", field2="darren", type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED
    )
    req2 = UserRequest(
        field1="darren", field2="cillian", type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED
    )
    req3 = UserRequest(
        field1="cillian", field2="roisin", type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED
    )
    req4 = UserRequest(
        field1="roisin", field2="cillian", type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED
    )
    req5 = UserRequest(
        field1="cillian", field2="joana", type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED
    )
    req6 = UserRequest(
        field1="joana", field2="cillian", type=RequestTypes.FOLLOW_REQUEST, status=Status.PENDING
    )
    req7 = UserRequest(
        field1="cillian", field2="foodwise", type=RequestTypes.FOLLOW_REQUEST, status=Status.PENDING
    )
    req8 = UserRequest(
        field1="foodwise", field2="cillian", type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED
    )
    req9 = UserRequest(
        field1="cillian", field2="darren", type=RequestTypes.CIRCLE_INVITE, status=Status.ACCEPTED
    )
    req10 = UserRequest(
        field1="darren", field2="cillian", type=RequestTypes.CIRCLE_INVITE, status=Status.PENDING
    )
    event_invite1 = UserRequest(
        field1="cillian", field2="darren", field3=1, type=RequestTypes.EVENT_INVITE, status=Status.PENDING
    )
    db.add(user1)
    db.add(user2)
    db.add(user3)
    db.add(user4)
    db.add(user5)
    db.add(user1_details)
    db.add(user2_details)
    db.add(user3_details)
    db.add(user4_details)
    db.add(user5_details)
    db.add(event)
    db.add(req1)
    db.add(req2)
    db.add(req3)
    db.add(req4)
    db.add(req5)
    db.add(req6)
    db.add(req7)
    db.add(req8)
    db.add(req9)
    db.add(req10)
    db.add(event_invite1)
    db.commit()
    seed_cork_dummy_events()