from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from common.JWTSecurity import decode_and_verify
from common.clients.client import post, get
from forms import ChangeDetailsForm, LoginForm, RegisterForm, EditEventForm
from common.db.init import init_db
import os
from passlib.context import CryptContext
from datetime import datetime

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

AUTH_INTERNAL_BASE = os.getenv("AUTH_INTERNAL_BASE", "http://auth:8001")
CIRCLES_INTERNAL_BASE = os.getenv("CIRCLES_INTERNAL_BASE", "http://circles:8002")
EVENTS_INTERNAL_BASE = os.getenv("EVENTS_INTERNAL_BASE", "http://events:8005")
USER_INTERNAL_BASE = os.getenv("USER_INTERNAL_BASE", "http://user:8005")
EVENTS_INTERNAL_BASE = os.getenv("EVENTS_INTERNAL_BASE", "http://events:8005")

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

@app.get("/", response_class=HTMLResponse)
@app.get("/home", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"display_map": True}
    )

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

@app.get("/profile", response_class=HTMLResponse)
async def get_profile(request: Request, claims: dict = Depends(require_frontend_auth)):
    authorized_user = claims.get("sub")
    user_details_data = await get(AUTH_INTERNAL_BASE, "users/me", headers={"Cookie" : f"access_token={request.cookies.get('access_token')}"})
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
        request=request, name="circle.html", context={"friends_list": friends_list, "circle": circle, "pending_invites": pending_invites, "invitations_sent": invitations_sent}
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

# User Management Endpoints

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

# Invites

@app.get("/invites", response_class=HTMLResponse)
@app.get("/invites/{invite_type}", response_class=HTMLResponse)
async def get_invites(request: Request, invite_type: str | None = "all", claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    if not invite_type:
        invite_type = "all"
    if invite_type not in ["follow_requests", "circle_invites", "group_invites", "event_invites", "all"]:
        invite_type = "all"
    follow_requests = []
    circle_invites = []
    group_invites = []
    event_invites = []
    if invite_type == "follow_requests" or invite_type == "all":
        follow_request_data = await get(USER_INTERNAL_BASE, "get_follow_requests_received", headers={"Cookie" : f"access_token={token}"})
        follow_requests = follow_request_data.get("user_names", []) if follow_request_data is not None else []
    if invite_type == "circle_invites" or invite_type == "all":
        circle_invites_data = await get(CIRCLES_INTERNAL_BASE, "get_invites", headers={"Cookie" : f"access_token={token}"})
        circle_invites = circle_invites_data.get("user_names", []) if circle_invites_data is not None else []
    if invite_type == "group_invites" or invite_type == "all":
        group_invites_data = [] # await get(GROUP_INTERNAL_BASE, "get_group_invites", headers={"Cookie" : f"access_token={token}"})
        group_invites = [] #group_invites_data.get("group_names", []) if group_invites_data is not None else []
    if invite_type == "event_invites" or invite_type == "all":
        event_invites_data = [] #await get(EVENTS_INTERNAL_BASE, "get_invites", headers={"Cookie" : f"access_token={token}"})
        event_invites = [] #event_invites_data.get("event_names", []) if event_invites_data is not None else []
    return templates.TemplateResponse(
        request=request, name="invites.html", context={"follow_requests": follow_requests, 
                                                       "circle_invites": circle_invites, 
                                                       "group_invites": group_invites, 
                                                       "event_invites": event_invites}
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
    event_start_time = event_info_data.get("datetime_start", "Unknown Start Time")
    event_end_time = event_info_data.get("datetime_end", "Unknown End Time")   
    event_description = event_info_data.get("description", "No Description Available")
    event_public = event_info_data.get("public", False)
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
                                                          "is_user_host": is_user_host,
                                                          "is_user_invited_pending": is_user_invited_pending,
                                                          "is_user_attending": is_user_attending}
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

@app.get("/events/edit/{event_id}", response_class=HTMLResponse)
async def edit_event(request: Request, event_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    user = claims.get("sub")
    form= EditEventForm()
    event_info_data = await get(EVENTS_INTERNAL_BASE, f"eventinfo/{event_id}", headers={"Cookie" : f"access_token={token}"})
    if event_info_data is None or event_info_data.get("valid", True) == False   :
        return templates.TemplateResponse(
            request=request, name="forms/edit_event.html", context={"form": form, "error": "Event not found."}
        )
    if event_info_data.get("host") != user:
        return templates.TemplateResponse(
            request=request, name="forms/edit_event.html", context={"form": form, "error": "You are not the host of this event."}
        )
    if event_info_data:
        form.title.data = event_info_data.get("title", "")
        form.venue.data = event_info_data.get("venue", "")
        datetime_start_str = event_info_data.get("datetime_start")
        form.datetime_start.data = datetime.fromisoformat(datetime_start_str.replace("Z", "+00:00")) if datetime_start_str else None
        datetime_end_str = event_info_data.get("datetime_end")
        form.datetime_end.data = datetime.fromisoformat(datetime_end_str.replace("Z", "+00:00")) if datetime_end_str else None
        form.latitude.data = event_info_data.get("latitude", 0.0)
        form.longitude.data = event_info_data.get("longitude", 0.0)
        form.description.data = event_info_data.get("description", "")
    return templates.TemplateResponse(
        request=request, name="forms/edit_event.html", context={"form": form}
    )

@app.post("/events/edit/{event_id}", response_class=HTMLResponse)
async def post_edit_event(request: Request, event_id: int, claims: dict = Depends(require_frontend_auth)):
    data= await request.form()
    form = EditEventForm(data=data) 

    if not form.validate():
        for field, errors in form.errors.items():
            form.form_errors.extend(f"{field}: {error}" for error in errors)
        return templates.TemplateResponse(
            request=request, name="forms/edit_event.html", context={"form": form}, status_code=400
        )
    
    response= await post(EVENTS_INTERNAL_BASE, f"edit/{event_id}", headers={"Cookie" : f"access_token={request.cookies.get('access_token')}"},
                         json={
                                  "title": form.title.data,
                                  "venue": form.venue.data,
                                  "datetime_start": form.datetime_start.data,
                                  "datetime_end": form.datetime_end.data,
                                  "latitude": form.latitude.data,
                                  "longitude": form.longitude.data,
                                  "description": form.description.data
                               })
    if response is None or not response.get("valid", True):
        form.form_errors.append(response.get("message", "Event update failed."))
        return templates.TemplateResponse(
            request=request, name="forms/edit_event.html", context={"form": form}, status_code=401
        )
    response = RedirectResponse(url=f"/eventinfo/{event_id}", status_code=303)

    return response


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

@app.get("/events/attend/{event_id}", response_class=HTMLResponse)
async def attend_event(request: Request, event_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    user = claims.get("sub")
    await post(EVENTS_INTERNAL_BASE, f"attend/{event_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=f"/eventinfo/{event_id}", status_code=303)

@app.get("/events/decline/{event_id}", response_class=HTMLResponse)
async def decline_event_invite(request: Request, event_id: int, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    user = claims.get("sub")
    await post(EVENTS_INTERNAL_BASE, f"decline/{event_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url="/events", status_code=303)

# Follow Request Decline (alias for withdraw)
@app.get("/decline_follow/{username}", response_class=HTMLResponse)
async def decline_follow(request: Request, username: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    authorized_user = claims.get("sub")
    await post(USER_INTERNAL_BASE, "withdraw_follow_request", headers={"Cookie" : f"access_token={token}"}, 
                                             json={"inviter": username, "invitee": authorized_user}
                                             )
    return RedirectResponse(url=referer, status_code=303)

# Circle Invites
@app.get("/accept_circle_invite/{username}", response_class=HTMLResponse)
async def accept_circle_invite(request: Request, username: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    this_user = claims.get("sub")
    await post(CIRCLES_INTERNAL_BASE, "accept", headers={"Cookie" : f"access_token={token}"}, 
                                       json={"inviter": username, "invitee": this_user}
                                       )
    return RedirectResponse(url=referer, status_code=303)

@app.get("/decline_circle_invite/{username}", response_class=HTMLResponse)
async def decline_circle_invite(request: Request, username: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    this_user = claims.get("sub")
    await post(CIRCLES_INTERNAL_BASE, "decline", headers={"Cookie" : f"access_token={token}"}, 
                                        json={"inviter": username, "invitee": this_user}
                                        )
    return RedirectResponse(url=referer, status_code=303)

# Group Invites
@app.get("/accept_group_invite/{group_id}", response_class=HTMLResponse)
async def accept_group_invite(request: Request, group_id: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    this_user = claims.get("sub")
    # TODO: Implement group invite acceptance on backend
    # For now, just redirect back
    return RedirectResponse(url=referer, status_code=303)

@app.get("/decline_group_invite/{group_id}", response_class=HTMLResponse)
async def decline_group_invite(request: Request, group_id: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    this_user = claims.get("sub")
    # TODO: Implement group invite decline on backend
    # For now, just redirect back
    return RedirectResponse(url=referer, status_code=303)

# Event Invites
@app.get("/accept_event_invite/{event_id}", response_class=HTMLResponse)
async def accept_event_invite(request: Request, event_id: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    user = claims.get("sub")
    await post(EVENTS_INTERNAL_BASE, f"attend/{event_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=referer, status_code=303)

@app.get("/decline_event_invite/{event_id}", response_class=HTMLResponse)
async def decline_event_invite_from_invites(request: Request, event_id: str, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    referer = request.headers.get("referer", "/")
    user = claims.get("sub")
    await post(EVENTS_INTERNAL_BASE, f"decline/{event_id}", headers={"Cookie" : f"access_token={token}"})
    return RedirectResponse(url=referer, status_code=303)