from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import insert
from starlette.middleware.sessions import SessionMiddleware
from common.JWTSecurity import decode_and_verify
from common.clients.client import post, get
from common.clients.user import user_follow_requests, user_follower_requests, user_followers, user_following, user_friends
from common.db.db import get_db
from common.db.structures.structures import RequestTypes, Status, UserRequest
from forms import LoginForm, RegisterForm
from common.db.init import init_db
import os

templates = Jinja2Templates(directory="templates")

AUTH_INTERNAL_BASE = os.getenv("AUTH_INTERNAL_BASE", "http://auth:8001")
CIRCLES_INTERNAL_BASE = os.getenv("CIRCLES_INTERNAL_BASE", "http://circles:8002")

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
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"display_map": True}
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
    response = RedirectResponse(url=request.query_params.get("next", "/dashboard"), status_code=303)

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

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request : Request, claims : dict = Depends(require_frontend_auth)):
    #All temp for testing
    user_flw_reqs = user_follow_requests(claims.get("sub"))
    user_flwr_reqs = user_follower_requests(claims.get("sub"))
    friends = user_friends(claims.get("sub"))
    return templates.TemplateResponse(
            request=request, name="dashboard.html", context={"user" : claims.get("sub"),
                                                             "user_flw_reqs" : user_flw_reqs,
                                                             "user_flwr_reqs" : user_flwr_reqs,
                                                             "friends" : friends}
        )

@app.get("/community", response_class=HTMLResponse)
async def get_community(request : Request, claims : dict = Depends(require_frontend_auth)):
    #All temp for testing
    user_flw_reqs = user_follow_requests(claims.get("sub"))
    user_flwr_reqs = user_follower_requests(claims.get("sub"))
    friends = user_friends(claims.get("sub"))
    return templates.TemplateResponse(
            request=request, name="community.html", context={"user" : claims.get("sub"),
                                                             "user_flw_reqs" : user_flw_reqs,
                                                             "user_flwr_reqs" : user_flwr_reqs,
                                                             "friends" : friends}
        )

@app.get("/circle", response_class=HTMLResponse)
async def get_circle(request: Request, claims: dict = Depends(require_frontend_auth)):
    token = request.cookies.get("access_token")
    friends = user_friends(claims.get("sub"))
    mycircle_data = await get(CIRCLES_INTERNAL_BASE, "mycircle", headers={"Cookie" : f"access_token={token}"})
    circle = mycircle_data.get("user_names", []) if mycircle_data else []
    pending_invites_data = await get(CIRCLES_INTERNAL_BASE, "get_invites", headers={"Cookie" : f"access_token={token}"})
    pending_invites = pending_invites_data.get("user_names", []) if pending_invites_data else []
    invitations_sent_data = await get(CIRCLES_INTERNAL_BASE, "get_invites_sent", headers={"Cookie" : f"access_token={token}"})
    invitations_sent = invitations_sent_data.get("user_names", []) if invitations_sent_data else [] 
    return templates.TemplateResponse(
        request=request, name="circle.html", context={"friends": friends, "circle": circle, "pending_invites": pending_invites, "invitations_sent": invitations_sent}
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
    this_user = claims.get("sub")
    if this_user == username:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    db = get_db()
    stmt = insert(UserRequest).values(field1=claims.get("sub"), 
                                      field2=username, 
                                      type=RequestTypes.FOLLOW_REQUEST, 
                                      status=Status.PENDING)
    db.execute(stmt)
    return RedirectResponse(
        url=request.url, 
        status_code=status.HTTP_303_SEE_OTHER,
        headers={"Cookie" : f"access_token={token}"}
    )