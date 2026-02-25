from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from common.JWTSecurity import decode_and_verify
from common.clients.client import post, get
from forms import ChangeDetailsForm, EventForm, GroupForm, LoginForm, RegisterForm
from common.db.init import init_db
import os
from passlib.context import CryptContext
from datetime import datetime

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

AUTH_INTERNAL_BASE = os.getenv("AUTH_INTERNAL_BASE", "http://auth:8001")
CIRCLES_INTERNAL_BASE = os.getenv("CIRCLES_INTERNAL_BASE", "http://circles:8002")
GROUPS_INTERNAL_BASE = os.getenv("GROUPS_INTERNAL_BASE", "http://groups:8003")
EVENTS_INTERNAL_BASE = os.getenv("EVENTS_INTERNAL_BASE", "http://events:8005")
USER_INTERNAL_BASE = os.getenv("USER_INTERNAL_BASE", "http://user:8006")

app = FastAPI(title="frontend_service")
init_db()

#This basically allows us to hold JWT's in a session, a soft substitute for Flask's "g" object
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("JWT_SECRET", "rosebud"),
    same_site="lax",
    https_only=False,  # True in production behind HTTPS
)

#Tells the frontend app where the static resources are
app.mount(
    "/static", 
    StaticFiles(directory="static"), 
    name="static"
)

def require_frontend_auth(request: Request) -> dict:
    token = request.cookies.get("access_token")
    
    if not token:
        print("DEBUG: No access_token found in cookies")
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": f"/login?next={request.url.path}"}
        )

    try:
        return decode_and_verify(token=token, expected_type="access")
    except Exception as e:
        print(f"DEBUG: Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": f"/login?next={request.url.path}"}
        )
    
def is_logged_in(request: Request) -> bool | None:
    token = request.cookies.get("access_token")
    if not token:
        return False
    try:
        claims = decode_and_verify(token, expected_type="access")
        return (claims is not None)
    except Exception as e:
        return False

@app.get("/", response_class=HTMLResponse)
@app.get("/home", response_class=HTMLResponse)
async def index(request: Request):
    authorized_user = None
    token = request.cookies.get("access_token")
    if token:
        try:
            claims = decode_and_verify(token=token, expected_type="access")
            authorized_user = claims.get("sub")
        except Exception:
            authorized_user = None
    return templates.TemplateResponse(
        request=request, name="home.html", context={"display_map": True, "authorized_user": authorized_user}
    )

# Authentication Endpoints

@app.get("/register", response_class=HTMLResponse)
async def get_register(request: Request):
    form = RegisterForm()
    return templates.TemplateResponse(
        request=request, name="forms/register.html", context={"form" : form}
    )

@app.post("/register", response_class=HTMLResponse)
async def post_register(request : Request):
    data = await request.form()
    form = RegisterForm(data=data)

    if not form.validate():
        print("DEBUG: Form validation failed with errors:", form.errors)
        for field, errors in form.errors.items():
            form.form_errors.extend(f"{field}: {error}" for error in errors)
        return templates.TemplateResponse(
            request=request, name="forms/register.html", context={"form" : form}, status_code=400
        )
    print("DEBUG: Form validated successfully with data:", form.data)
    response = await post(AUTH_INTERNAL_BASE, "register", json={"username": form.username.data, 
                                                                  "password": form.password.data, 
                                                                  "email": form.email.data,
                                                                  "phone_number": form.phone_number.data})
    print("DEBUG: Received response from auth service:", response)
    if response is None or not response.get("valid", True):
        print("DEBUG: Registration failed, no response from auth service")
        form.form_errors.append(response.get("message", "Registration failed."))
        return templates.TemplateResponse(
            request=request, name="forms/register.html", context={"form" : form}, status_code=401
        )
    print("DEBUG: Registration successful, redirecting to login")
    response = RedirectResponse(url=request.query_params.get("next", "/login"), status_code=303)

    return response

@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    form = LoginForm()
    return templates.TemplateResponse(
        request=request, name="forms/login.html", context={"form" : form}
    )

@app.post("/login", response_class=HTMLResponse)
async def post_login(request : Request):
    data = await request.form()
    form = LoginForm(data=data)

    # Check form was correctly filled
    if not form.validate():
        return templates.TemplateResponse(
            request=request, name="forms/login.html", context={"form" : form}, status_code=400
        )
    
    # Run auth microservice to get token
    token_payload = await post(AUTH_INTERNAL_BASE, "login", json={"username": form.username.data, 
                                                                  "password": form.password.data})
    if token_payload is None:
        form.username.errors.append("Invalid username or password.")
        return templates.TemplateResponse(
            request=request, name="forms/login.html", context={"form" : form}, status_code=401
        )
    response = RedirectResponse(url=request.query_params.get("next", "/community"), status_code=303)

    response.set_cookie(
        key="access_token",
        value=token_payload["access_token"],
        httponly=True,
        path="/",
        samesite="lax",
    )
    if token_payload.get("refresh_token"):
        response.set_cookie(
        key="refresh_token",
        value=token_payload["refresh_token"],
        httponly=True,
        path="/",
        samesite="lax",
    )

    return response

@app.get("/logout")
async def logout(request: Request):
    if not request.cookies.get("access_token") and not request.cookies.get("refresh_token"):
        return RedirectResponse(url="/login", status_code=303)
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return response

# User Interface Endpoints

@app.get("/profile/{username}", response_class=HTMLResponse)
@app.get("/profile", response_class=HTMLResponse)
async def get_profile(request: Request, username: str = None, claims: dict = Depends(require_frontend_auth)):
    authorized_user = claims.get("sub")
    user_details_data = await get(AUTH_INTERNAL_BASE, f"users/{username}" if username else "users/me", headers={"Cookie" : f"access_token={request.cookies.get('access_token')}"})
    user_details = user_details_data if user_details_data else None
    return templates.TemplateResponse(
        request=request, name="profile.html", context={"authorized_user": authorized_user, 
                                                       "user_details": user_details}
    )

@app.get("/change_details", response_class=HTMLResponse)
async def get_change_details(request: Request, claims: dict = Depends(require_frontend_auth)):
    form = ChangeDetailsForm()
    user_details_data = await get(AUTH_INTERNAL_BASE, "users/me", headers={"Cookie" : f"access_token={request.cookies.get('access_token')}"})
    user_details = user_details_data if user_details_data else None
    if user_details:
        form.first_name.data = user_details.get("first_name", "")
        form.last_name.data = user_details.get("last_name", "")
        form.email.data = user_details.get("email", "")
        form.phone_number.data = user_details.get("phone_number", "")
    return templates.TemplateResponse(
        request=request, name="forms/change_details.html", context={"form" : form}
    )

@app.post("/change_details", response_class=HTMLResponse)
async def post_change_details(request: Request, claims: dict = Depends(require_frontend_auth)):
    data = await request.form()
    form = ChangeDetailsForm(data=data)

    if not form.validate():
        for field, errors in form.errors.items():
            form.form_errors.extend(f"{field}: {error}" for error in errors)
        return templates.TemplateResponse(
            request=request, name="forms/change_details.html", context={"form" : form}, status_code=400
        )
    
    response = await post(AUTH_INTERNAL_BASE, "users/me", headers={"Cookie" : f"access_token={request.cookies.get('access_token')}"}, 
                                                          json={
                                                                  "first_name": form.first_name.data,
                                                                  "last_name": form.last_name.data,
                                                                  "email": form.email.data,
                                                                  "phone_number": form.phone_number.data})
    
    if response is None or not response.get("valid", True):
        form.form_errors.append(response.get("message", "Update failed."))
        return templates.TemplateResponse(
            request=request, name="forms/change_details.html", context={"form" : form}, status_code=401
        )

    response = RedirectResponse(url=request.query_params.get("next", "/profile"), status_code=303)

    return response

@app.get("/community", response_class=HTMLResponse)
async def get_community(request : Request, claims : dict = Depends(require_frontend_auth)):
    follow_requests_sent_data = await get(USER_INTERNAL_BASE, "get_follow_requests_sent", 
                              headers={"Cookie" : f"access_token={request.cookies.get('access_token')}"})
    follow_requests_sent = follow_requests_sent_data.get("user_names", []) if follow_requests_sent_data is not None else []

    follow_requests_received_data = await get(USER_INTERNAL_BASE, "get_follow_requests_received", 
                               headers={"Cookie" : f"access_token={request.cookies.get('access_token')}"})
    follow_requests_received = follow_requests_received_data.get("user_names", []) if follow_requests_received_data is not None else []
    
    friends_list_data = await get(USER_INTERNAL_BASE, "friends", 
                        headers={"Cookie" : f"access_token={request.cookies.get('access_token')}"})
    friends_list = friends_list_data.get("user_names", []) if friends_list_data is not None else []

    all_users_data = await get(USER_INTERNAL_BASE, "list_users", headers={"Cookie" : f"access_token={request.cookies.get('access_token')}"})
    all_users = all_users_data.get("user_names", []) if all_users_data is not None else []

    authorized_user = claims.get("sub")
    
    return templates.TemplateResponse(
            request=request, name="community.html", context={"authorized_user" : authorized_user,
                                                             "follow_requests_sent" : follow_requests_sent,
                                                             "follow_requests_received" : follow_requests_received,
                                                             "friends_list" : friends_list,
                                                             "all_users" : all_users}
    )

@app.get("/invites", response_class=HTMLResponse)
@app.get("/invites/{invite_type}", response_class=HTMLResponse)
async def get_invites(request: Request, invite_type: str | None = "all", claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    if not invite_type:
        invite_type = "all"
    if invite_type not in ["event_requests", "group_requests", "follow_requests", "circle_invites", "group_invites", "event_invites", "all"]:
        invite_type = "all"
    follow_requests = []
    circle_invites = []
    group_invites = []
    event_invites = []
    event_requests = []
    group_requests = []
    if invite_type == "follow_requests" or invite_type == "all":
        follow_request_data = await get(USER_INTERNAL_BASE, "get_follow_requests_received", headers={"Cookie" : f"access_token={token}"})
        follow_requests = follow_request_data.get("user_names", []) if follow_request_data is not None else []
    if invite_type == "circle_invites" or invite_type == "all":
        circle_invites_data = await get(CIRCLES_INTERNAL_BASE, "get_invites", headers={"Cookie" : f"access_token={token}"})
        circle_invites = circle_invites_data.get("user_names", []) if circle_invites_data is not None else []
    if invite_type == "group_invites" or invite_type == "all":
        group_invites_data = await get(GROUPS_INTERNAL_BASE, "get_group_invites", headers={"Cookie" : f"access_token={token}"})
        group_invites_raw = group_invites_data.get("invites", []) if group_invites_data is not None else []
        group_invites = [{"group_id": req["group_id"], "group_name": req["group_name"], "username": req["username"]} for req in group_invites_raw]
    if invite_type == "group_requests" or invite_type == "all":
        group_requests_data = await get(GROUPS_INTERNAL_BASE, "get_group_requests", headers={"Cookie" : f"access_token={token}"})
        group_requests_raw = group_requests_data.get("invites", []) if group_requests_data is not None else []
        group_requests = [{"group_id": req["group_id"], "group_name": req["group_name"], "username": req["username"]} for req in group_requests_raw]
    if invite_type == "event_invites" or invite_type == "all":
        event_invites_data = await get(EVENTS_INTERNAL_BASE, "my_invites", headers={"Cookie" : f"access_token={token}"})
        invited_events = event_invites_data.get("events", []) if event_invites_data is not None else []
        event_invites = [{"id": event["id"], "title": event["title"]} for event in invited_events]
    if invite_type == "event_requests" or invite_type == "all":
        event_requests_data = await get(EVENTS_INTERNAL_BASE, "my_event_requests", headers={"Cookie" : f"access_token={token}"})
        event_requests_raw = event_requests_data.get("requests", []) if event_requests_data is not None else []
        event_requests = [{"id": req["event_id"], "title": req["title"], "username": req["username"]} for req in event_requests_raw]
    return templates.TemplateResponse(
        request=request, name="invites.html", context={"follow_requests": follow_requests, 
                                                       "circle_invites": circle_invites, 
                                                       "group_invites": group_invites, 
                                                       "group_requests": group_requests,
                                                       "event_invites": event_invites,
                                                       "event_requests": event_requests}
    )

# Event Management Endpoints

@app.get("/eventinfo/{event_id}", response_class=HTMLResponse)
async def event_info(request: Request, event_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    user = claims.get("sub")
    is_user_host_data = await get(EVENTS_INTERNAL_BASE, f"is_host/{event_id}/{user}", headers={"Cookie" : f"access_token={token}"})
    is_user_host = is_user_host_data.get("value", False) if is_user_host_data else False
    is_user_invited_pending_data = await get(EVENTS_INTERNAL_BASE, f"is_invited_pending/{event_id}/{user}", headers={"Cookie" : f"access_token={token}"})
    is_user_invited_pending = is_user_invited_pending_data.get("value", False) if is_user_invited_pending_data else False
    is_user_attending_data = await get(EVENTS_INTERNAL_BASE, f"is_attending/{event_id}/{user}", headers={"Cookie" : f"access_token={token}"})
    is_user_attending = is_user_attending_data.get("value", False) if is_user_attending_data else False
    is_user_requested_data = await get(EVENTS_INTERNAL_BASE, f"is_requested/{event_id}/{user}")
    is_user_attending = is_user_attending or is_user_host
    is_user_requested = is_user_requested_data.get("value", False) if is_user_requested_data else False
    event_info_data = await get(EVENTS_INTERNAL_BASE, f"eventinfo/{event_id}", headers={"Cookie" : f"access_token={token}"})
    if event_info_data is None or event_info_data.get("valid", True) == False:
        return templates.TemplateResponse(
            request=request, name="event_info.html", context={"error": "Event not found."}
        )
    event_name = event_info_data.get("title", "Unknown Event")
    event_venue = event_info_data.get("venue", "Unknown Venue")
    event_host = event_info_data.get("host", "Unknown Host")
    event_latitude = event_info_data.get("latitude", "Unknown Latitude")
    event_longitude = event_info_data.get("longitude", "Unknown Longitude")
    event_start_time = "Unknown Start Time"
    event_end_time = "Unknown End Time"
    if isinstance(event_info_data.get("datetime_start"), str):
        try:
            event_start_time = datetime.fromisoformat(event_info_data["datetime_start"].replace("Z", "+00:00"))
        except Exception as e:
            print(f"DEBUG: Failed to parse datetime_start: {e}")
            event_start_time = "Unknown Start Time"
    if isinstance(event_info_data.get("datetime_end"), str):
        try:
            event_end_time = datetime.fromisoformat(event_info_data["datetime_end"].replace("Z", "+00:00"))
        except Exception as e:
            print(f"DEBUG: Failed to parse datetime_end: {e}")
            event_end_time = "Unknown End Time"
    event_description = event_info_data.get("description", "No Description Available")
    event_public = event_info_data.get("public", False)

    my_groups_data = await get(GROUPS_INTERNAL_BASE, "mygroups", headers={"Cookie" : f"access_token={token}"})
    my_groups = my_groups_data.get("group_list", []) if my_groups_data else []

    return templates.TemplateResponse(
        request=request, name="event_info.html", context={"event_id": event_id,
                                                          "event_title": event_name, 
                                                          "event_venue": event_venue, 
                                                          "event_host": event_host, 
                                                          "event_latitude": event_latitude, 
                                                          "event_longitude": event_longitude, 
                                                          "event_start_time": event_start_time, 
                                                          "event_end_time": event_end_time, 
                                                          "event_description": event_description,
                                                          "event_public": event_public,
                                                          "is_host": is_user_host,
                                                          "is_invited": is_user_invited_pending,
                                                          "is_attending": is_user_attending,
                                                          "is_requested" : is_user_requested,
                                                          "my_groups": my_groups}
    )

@app.get("/events", response_class=HTMLResponse)
async def all_events(request: Request, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    all_events_data = await get(EVENTS_INTERNAL_BASE, "all_events", headers={"Cookie" : f"access_token={token}"})
    all_events_info = [] if all_events_data is None else all_events_data.get("events", [])
    all_events = []
    for event in all_events_info:
        all_events.append({
            "id": event["id"],
            "title": event["title"],
            "venue": event["venue"],
            "latitude": event["latitude"],
            "longitude": event["longitude"],
            "start_time": event["datetime_start"],
            "end_time": event["datetime_end"],
            "host": event["host"],
            "description": event["description"]
        })
    
    return templates.TemplateResponse(
        request=request, name="events_map.html", context={"all_events": all_events, "display_map": True}
    )

@app.get("/events/create_event", response_class=HTMLResponse)
async def get_create_event(request : Request, claims : dict = Depends(require_frontend_auth)):
    form = EventForm()
    return templates.TemplateResponse(
        request=request, name="forms/edit_event.html", context={"form": form, "display_map": True}
    )

@app.post("/events/create_event", response_class=HTMLResponse)
async def post_create_event(request: Request, claims: dict = Depends(require_frontend_auth)):
    data = await request.form()
    print(f"RAW FORM DATA: {data}")
    form = EventForm(formdata=data) 

    if not form.validate():
        for field, errors in form.errors.items():
            form.form_errors.extend(f"{field}: {error}" for error in errors)
        return templates.TemplateResponse(
            request=request, name="forms/edit_event.html", context={"form": form, "display_map": True}, status_code=400
        )
    
    print("DEBUG: Form validated successfully with data:", form.data)
    
    response= await post(EVENTS_INTERNAL_BASE, "create", 
                        headers={"Cookie" : f"access_token={request.cookies.get('access_token')}"},
                        json={
                                "title": form.title.data,
                                "venue": form.venue.data,
                                "datetime_start": form.datetime_start.data.isoformat(),
                                "datetime_end": form.datetime_end.data.isoformat(),
                                "latitude": form.latitude.data,
                                "longitude": form.longitude.data,
                                "description": form.description.data,
                                "public": form.is_public.data
                            })
    print("DEBUG: Received response from event service:", response)
    if response is None:
        form.form_errors.append("Event creation failed. No response from event service.")
        return templates.TemplateResponse(
            request=request, name="forms/edit_event.html", context={"form": form, "display_map": True}, status_code=401
        )
    response = RedirectResponse(url=f"/eventinfo/{response.get('event_id')}", status_code=303)
    return response

@app.get("/events/edit/{event_id}", response_class=HTMLResponse)
async def edit_event(request: Request, event_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    user = claims.get("sub")
    form = EventForm()
    event_info_data = await get(EVENTS_INTERNAL_BASE, f"eventinfo/{event_id}", headers={"Cookie" : f"access_token={token}"})
    if event_info_data is None or event_info_data.get("valid", True) == False   :
        return templates.TemplateResponse(
            request=request, name="forms/edit_event.html", context={"form": form, "error": "Event not found.", "display_map": True}
        )
    if event_info_data.get("host") != user:
        return templates.TemplateResponse(
            request=request, name="forms/edit_event.html", context={"form": form, "error": "You are not the host of this event.", "display_map": True}
        )
    if event_info_data:
        form.title.data = event_info_data.get("title", "")
        form.venue.data = event_info_data.get("venue", "")
        event_start_time = "Unknown Start Time"
        event_end_time = "Unknown End Time"
        if isinstance(event_info_data.get("datetime_start"), str):
            try:
                event_start_time = datetime.fromisoformat(event_info_data["datetime_start"].replace("Z", "+00:00"))
            except Exception as e:
                print(f"DEBUG: Failed to parse datetime_start: {e}")
                event_start_time = "Unknown Start Time"
        if isinstance(event_info_data.get("datetime_end"), str):
            try:
                event_end_time = datetime.fromisoformat(event_info_data["datetime_end"].replace("Z", "+00:00"))
            except Exception as e:
                print(f"DEBUG: Failed to parse datetime_end: {e}")
                event_end_time = "Unknown End Time"
        form.datetime_start.data = event_start_time
        form.datetime_end.data = event_end_time
        form.latitude.data = event_info_data.get("latitude", 0.0)
        form.longitude.data = event_info_data.get("longitude", 0.0)
        form.description.data = event_info_data.get("description", "")
        form.is_public.data = event_info_data.get("public", False)
    return templates.TemplateResponse(
        request=request, name="forms/edit_event.html", context={"form": form, "display_map": True}
    )

@app.post("/events/edit/{event_id}", response_class=HTMLResponse)
async def post_edit_event(request: Request, event_id: int, claims: dict = Depends(require_frontend_auth)):
    data= await request.form()
    form = EventForm(formdata=data) 

    if not form.validate():
        for field, errors in form.errors.items():
            form.form_errors.extend(f"{field}: {error}" for error in errors)
        return templates.TemplateResponse(
            request=request, name="forms/edit_event.html", context={"form": form, "display_map": True}, status_code=400
        )
    
    response= await post(EVENTS_INTERNAL_BASE, f"edit/{event_id}", 
                         headers={"Cookie" : f"access_token={request.cookies.get('access_token')}"},
                         json={
                                "title": form.title.data,
                                "venue": form.venue.data,
                                "datetime_start": form.datetime_start.data.isoformat(),
                                "datetime_end": form.datetime_end.data.isoformat(),
                                "latitude": form.latitude.data,
                                "longitude": form.longitude.data,
                                "description": form.description.data,
                                "public": form.is_public.data
                               })
    if response is None or not response.get("valid", True):
        form.form_errors.append(response.get("message", "Event update failed."))
        return templates.TemplateResponse(
            request=request, name="forms/edit_event.html", context={"form": form, "display_map": True}, status_code=401
        )
    response = RedirectResponse(url=f"/eventinfo/{event_id}", status_code=303)

    return response

@app.get("/events/my_events", response_class=HTMLResponse)
async def my_events(request: Request, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    attending_events_data = await get(EVENTS_INTERNAL_BASE, f"myevents", headers={"Cookie" : f"access_token={token}"})
    attending_events = attending_events_data.get("events", []) if attending_events_data else []

    user = claims.get("sub")
    hosting_events_data = await get(EVENTS_INTERNAL_BASE, f"events_hosted_by/{user}", headers={"Cookie" : f"access_token={token}"})
    hosting_events = hosting_events_data.get("events", []) if hosting_events_data else []

    return templates.TemplateResponse(
        request=request, name="myevents.html", context={"attending_events": attending_events, "hosting_events": hosting_events}
    )

@app.get("/events/cancel/{event_id}", response_class=HTMLResponse)
async def cancel_event(request: Request, event_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    user = claims.get("sub")
    await post(EVENTS_INTERNAL_BASE, f"cancel/{event_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url="/events", status_code=303)

@app.get("/events/invitecircle/{event_id}/", response_class=HTMLResponse)
async def invite_circle_to_event(request: Request, event_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    await post(EVENTS_INTERNAL_BASE, f"invitecircle/{event_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=f"/eventinfo/{event_id}", status_code=303)

@app.get("/events/invite_group/{event_id}/{group_id}", response_class=HTMLResponse)
async def invite_group_to_event(request: Request, event_id: int, group_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    await post(EVENTS_INTERNAL_BASE, f"invite_group/{event_id}/{group_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=f"/eventinfo/{event_id}", status_code=303)

@app.get("/events/attend/{event_id}", response_class=HTMLResponse)
async def attend_event(request: Request, event_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    await post(EVENTS_INTERNAL_BASE, f"attend/{event_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=f"/eventinfo/{event_id}", status_code=303)

@app.get("/events/request/{event_id}", response_class=HTMLResponse)
async def request_to_attend_event(request: Request, event_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    await post(EVENTS_INTERNAL_BASE, f"request/{event_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=f"/eventinfo/{event_id}", status_code=303)

@app.get("/events/accept/{event_id}/{user}", response_class=HTMLResponse)
async def attend_event(request: Request, event_id: int, user: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    await post(EVENTS_INTERNAL_BASE, f"accept/{event_id}/{user}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=f"/eventinfo/{event_id}", status_code=303)

@app.get("/events/decline/{event_id}", response_class=HTMLResponse)
async def decline_event_invite(request: Request, event_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    await post(EVENTS_INTERNAL_BASE, f"decline/{event_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url="/events", status_code=303)

# User Management Endpoints

@app.get("/decline_follow/{username}", response_class=HTMLResponse)
async def decline_follow(request: Request, username: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    authorized_user = claims.get("sub")
    await post(USER_INTERNAL_BASE, "withdraw_follow_request", headers={"Cookie" : f"access_token={token}"}, 
                                             json={"inviter": username, "invitee": authorized_user}
                                             )
    return RedirectResponse(url=referer, status_code=303)

@app.get("/follow/{username}")
async def follow_user(request: Request, username: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    this_user = claims.get("sub")
    await post(USER_INTERNAL_BASE, "send_follow_request", headers={"Cookie" : f"access_token={token}"}, 
                                             json={"inviter": this_user, "invitee": username}
                                             )
    return RedirectResponse(url=referer, status_code=303)

@app.get("/accept_follow/{username}")
async def accept_follow(request: Request, username: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    this_user = claims.get("sub")
    await post(USER_INTERNAL_BASE, "accept_follow_request", headers={"Cookie" : f"access_token={token}"}, 
                                             json={"inviter": username, "invitee": this_user}
                                             )
    return RedirectResponse(url=referer, status_code=303)

@app.get("/withdraw/{username}")
async def withdraw_follow(request: Request, username: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    authorized_user = claims.get("sub")
    await post(USER_INTERNAL_BASE, "withdraw_follow_request", headers={"Cookie" : f"access_token={token}"}, 
                                             json={"inviter": authorized_user, "invitee": username}
                                             )
    return RedirectResponse(url=referer, status_code=303)

# Circle Management Endpoints

@app.get("/circle", response_class=HTMLResponse)
async def get_circle(request: Request, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")

    friends_list_data = await get(USER_INTERNAL_BASE, "friends", 
                        headers={"Cookie" : f"access_token={request.cookies.get('access_token')}"})
    friends_list = friends_list_data.get("user_names", []) if friends_list_data is not None else []

    mycircle_data = await get(CIRCLES_INTERNAL_BASE, "mycircle", headers={"Cookie" : f"access_token={token}"})
    circle = mycircle_data.get("user_names", []) if mycircle_data else []

    pending_invites_data = await get(CIRCLES_INTERNAL_BASE, "get_invites", headers={"Cookie" : f"access_token={token}"})
    pending_invites = pending_invites_data.get("user_names", []) if pending_invites_data else []

    invitations_sent_data = await get(CIRCLES_INTERNAL_BASE, "get_invites_sent", headers={"Cookie" : f"access_token={token}"})
    invitations_sent = invitations_sent_data.get("user_names", []) if invitations_sent_data else [] 

    return templates.TemplateResponse(
        request=request, name="circle.html", context={"friends": friends_list, "circle": circle, "pending_invites": pending_invites, "invitations_sent": invitations_sent}
    )

@app.get("/circle/invite_to_circle/{username}", response_class=HTMLResponse)
async def invite_to_circle(request: Request, username: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    await post(CIRCLES_INTERNAL_BASE, "invite", headers={"Cookie" : f"access_token={token}"}, json={"inviter": claims.get("sub"), "invitee": username})
    return RedirectResponse(url="/circle", status_code=303)

@app.get("/circle/accept/{username}", response_class=HTMLResponse)
async def accept_invite(request: Request, username: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    await post(CIRCLES_INTERNAL_BASE, "accept", headers={"Cookie" : f"access_token={token}"}, json={"inviter": username, "invitee": claims.get("sub")})
    return RedirectResponse(url="/circle", status_code=303)

@app.get("/circle/remove_from_circle/{username}", response_class=HTMLResponse)
async def remove_from_circle(request: Request, username: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    await post(CIRCLES_INTERNAL_BASE, "remove", headers={"Cookie" : f"access_token={token}"}, json={"inviter": claims.get("sub"), "invitee": username})
    return RedirectResponse(url="/circle", status_code=303) 

@app.get("/circle/decline/{username}", response_class=HTMLResponse)
async def decline_invite(request: Request, username: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    await post(CIRCLES_INTERNAL_BASE, "decline", headers={"Cookie" : f"access_token={token}"}, json={"inviter": username, "invitee": claims.get("sub")})
    return RedirectResponse(url="/circle", status_code=303)

# Group Management Endpoints

@app.get("/groups", response_class=HTMLResponse)
async def get_groups(request: Request, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    my_groups_data = await get(GROUPS_INTERNAL_BASE, "mygroups", headers={"Cookie" : f"access_token={token}"})
    my_groups = my_groups_data.get("group_list", []) if my_groups_data else []
    all_groups_data = await get(GROUPS_INTERNAL_BASE, "list", headers={"Cookie" : f"access_token={token}"})
    all_groups = all_groups_data.get("group_list", []) if all_groups_data else []
    return templates.TemplateResponse(
        request=request, name="groups.html", context={"my_groups": my_groups, "all_groups": all_groups}
    )

@app.get("/groups/create_group", response_class=HTMLResponse)
async def get_create_group(request: Request, claims: dict = Depends(require_frontend_auth)):
    form = GroupForm()
    return templates.TemplateResponse(
        request=request, name="forms/edit_group.html", context={"form": form}
    )

@app.post("/groups/create_group", response_class=HTMLResponse)
async def post_create_group(request: Request, claims: dict = Depends(require_frontend_auth)):
    data = await request.form()
    form = GroupForm(data=data)

    if not form.validate():
        return templates.TemplateResponse(
            request=request, name="forms/edit_group.html", context={"form": form}, status_code=400
        )
    
    token = request.cookies.get("access_token")
    response = await post(GROUPS_INTERNAL_BASE, "create", headers={"Cookie" : f"access_token={token}"}, 
                                            json={
                                                "group_name": form.group_name.data,
                                                "group_desc": form.group_desc.data,
                                                "is_private": not form.is_public.data
                                            })
    if response is None or not response.get("valid", True):
        form.form_errors.append(response.get("message", "Group creation failed."))
        return templates.TemplateResponse(
            request=request, name="forms/edit_group.html", context={"form": form}, status_code=401
        )
    group_id = response.get("group_id")
    return RedirectResponse(url=f"/groups/group_info/{group_id}", status_code=303)

@app.get("/groups/edit/{group_id}", response_class=HTMLResponse)
async def edit_group(request: Request, group_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    group_info_data = await get(GROUPS_INTERNAL_BASE, f"group_info/{group_id}", headers={"Cookie" : f"access_token={token}"})
    if group_info_data is None or group_info_data.get("valid", True) == False:
        return templates.TemplateResponse(
            request=request, name="forms/edit_group.html", context={"form": GroupForm(), "error": "Group not found."}
        )
    if group_info_data.get("owner") != claims.get("sub"):
        return templates.TemplateResponse(
            request=request, name="forms/edit_group.html", context={"form": GroupForm(), "error": "You are not the owner of this group."}
        )
    form = GroupForm()
    form.group_name.data = group_info_data.get("group_name", "")
    form.group_desc.data = group_info_data.get("group_desc", "")
    form.is_public.data = not group_info_data.get("is_private", False)
    return templates.TemplateResponse(
        request=request, name="forms/edit_group.html", context={"form": form}
    )

@app.post("/groups/edit/{group_id}", response_class=HTMLResponse)
async def post_edit_group(request: Request, group_id: int, claims: dict = Depends(require_frontend_auth)):
    data = await request.form()
    form = GroupForm(data=data)

    if not form.validate():
        return templates.TemplateResponse(
            request=request, name="forms/edit_group.html", context={"form": form}, status_code=400
        )
    
    token = request.cookies.get("access_token")
    response = await post(GROUPS_INTERNAL_BASE, f"edit/{group_id}", headers={"Cookie" : f"access_token={token}"}, 
                                            json={
                                                "group_name": form.group_name.data,
                                                "group_desc": form.group_desc.data,
                                                "is_private": not form.is_public.data
                                            })
    if response is None or not response.get("valid", True):
        form.form_errors.append(response.get("message", "Group update failed."))
        return templates.TemplateResponse(
            request=request, name="forms/edit_group.html", context={"form": form}, status_code=401
        )
    return RedirectResponse(url=f"/groups/group_info/{group_id}", status_code=303)

@app.get("/groups/group_info/{group_id}", response_class=HTMLResponse)
async def get_group_info(request: Request, group_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    group_info_data = await get(GROUPS_INTERNAL_BASE, f"group_info/{group_id}", headers={"Cookie" : f"access_token={token}"})
    group_id = group_info_data.get("group_id", -1) if group_info_data else -1
    if group_id == -1:
        return RedirectResponse(url="/groups", status_code=303)
    group_name = group_info_data.get("group_name", "Unknown Group") if group_info_data else "Unknown Group"
    group_description = group_info_data.get("group_desc", "No Description Available") if group_info_data else "No Description Available"
    group_members = group_info_data.get("members", []) if group_info_data else []
    group_owner = group_info_data.get("owner", "Unknown Owner") if group_info_data else "Unknown Owner"
    group_is_private = group_info_data.get("is_private", False) if group_info_data else False
    group_members_data = await get(GROUPS_INTERNAL_BASE, f"listmembers/{group_id}", headers={"Cookie" : f"access_token={token}"})
    group_members_list = group_members_data.get("members", []) if group_members_data else []
    group_members = [member.get("username", "Unknown User") for member in group_members_list]
    group = {
        "id": group_id,
        "group_name": group_name,
        "group_desc": group_description,
        "members": group_members,
        "owner": group_owner,
        "is_private": group_is_private
    }
    friends_list_data = await get(USER_INTERNAL_BASE, "friends", 
                        headers={"Cookie" : f"access_token={request.cookies.get('access_token')}"})
    friends_list = friends_list_data.get("user_names", []) if friends_list_data is not None else []

    user_has_requested = await get(GROUPS_INTERNAL_BASE, f"user_is_requested/{group_id}", headers={"Cookie" : f"access_token={token}"})
    user_is_invited = await get(GROUPS_INTERNAL_BASE, f"user_is_invited/{group_id}", headers={"Cookie" : f"access_token={token}"})

    join_requests = []
    if group_owner == claims.get("sub"):
        join_requests_data = await get(GROUPS_INTERNAL_BASE, f"get_this_group_requests/{group_id}", headers={"Cookie" : f"access_token={token}"})
        join_requests = join_requests_data.get("invites", []) if join_requests_data else []

    invitees = []
    if group_owner == claims.get("sub"):
        invitees_data = await get(GROUPS_INTERNAL_BASE, f"get_this_group_invites/{group_id}", headers={"Cookie" : f"access_token={token}"})
        invitees_raw = invitees_data.get("invites", []) if invitees_data else []
        for invite in invitees_raw:
            invitees.append(invite.get("username", "Unknown User"))

    return templates.TemplateResponse(
        request=request, name="group_info.html", context={"group": group, 
                                                          "group_members": group_members, 
                                                          "authorized_user": claims.get("sub"), 
                                                          "friends_list": friends_list,
                                                          "user_has_requested": user_has_requested,
                                                          "user_is_invited": user_is_invited,
                                                          "join_requests": join_requests,
                                                          "invitees": invitees }
    )

@app.get("/groups/join/{group_id}", response_class=HTMLResponse)
async def join_public_group(request: Request, group_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    response = await post(GROUPS_INTERNAL_BASE, f"join_public_group/{group_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=referer, status_code=303)

@app.get("/groups/invite/{username}/{group_id}", response_class=HTMLResponse)
async def accept_group_invite(request: Request, group_id: int, username: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    response = await post(GROUPS_INTERNAL_BASE, f"invite/{username}/{group_id}", headers={"Cookie" : f"access_token={token}"}, json={"invitee": username})
    return RedirectResponse(url=referer, status_code=303)

@app.get("/groups/accept_invite/{group_id}", response_class=HTMLResponse)
async def accept_group_invite(request: Request, group_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    response = await post(GROUPS_INTERNAL_BASE, f"accept_invite/{group_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=referer, status_code=303)

@app.get("/groups/decline_invite/{group_id}", response_class=HTMLResponse)
async def decline_group_invite(request: Request, group_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    response = await post(GROUPS_INTERNAL_BASE, f"decline_invite/{group_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=referer, status_code=303)

@app.get("/groups/request/{group_id}", response_class=HTMLResponse)
async def request_to_join_group(request: Request, group_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    response = await post(GROUPS_INTERNAL_BASE, f"request/{group_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=referer, status_code=303)

@app.get("/groups/accept_request/{group_id}/{user}", response_class=HTMLResponse)
async def accept_group_request(request: Request, group_id: int, user: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    response = await post(GROUPS_INTERNAL_BASE, f"accept_request/{group_id}/{user}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=referer, status_code=303)

@app.get("/groups/decline_request/{group_id}/{user}", response_class=HTMLResponse)
async def decline_request_group(request: Request, group_id: int, user: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    response = await post(GROUPS_INTERNAL_BASE, f"decline_request/{group_id}/{user}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=referer, status_code=303)

@app.get("/groups/leave/{group_id}", response_class=HTMLResponse)
async def leave_group(request: Request, group_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    response = await post(GROUPS_INTERNAL_BASE, f"leave/{group_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=referer, status_code=303)

@app.get("/groups/remove/{group_id}/{username}", response_class=HTMLResponse)
async def remove_from_group(request: Request, group_id: int, username: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    response = await post(GROUPS_INTERNAL_BASE, f"remove/{group_id}/{username}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=referer, status_code=303)

@app.get("/groups/delete/{group_id}", response_class=HTMLResponse)
async def delete_group(request: Request, group_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    response = await post(GROUPS_INTERNAL_BASE, f"delete/{group_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url="/groups", status_code=303)
