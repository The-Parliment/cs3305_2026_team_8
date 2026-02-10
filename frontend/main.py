from fastapi import Depends, FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from common.JWTSecurity import decode_and_verify
from common.clients.client import post
from common.clients.user import user_follow_requests, user_follower_requests, user_followers, user_following, user_friends
from forms import LoginForm
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
    secret_key=os.getenv("SESSION_SECRET", "rosebud"),
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
    '''
    Protects frontend routes.
    Reads JWT from frontend session cookie, verifies with common.decode_and_verify.
    Redirects to /login if invalid/expired.
    '''
    access = request.session.get("access_token")
    if not access:
        raise RedirectResponse(url="/login", status_code=303)

    try:
        claims = decode_and_verify(access, expected_type="access")
    except ValueError:
        request.session.clear()
        raise RedirectResponse(url="/login", status_code=303)

    return claims

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"display_map": True}
    )


@app.get("/login", name="login", response_class=HTMLResponse)
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
    
    request.session["access_token"] = token_payload["access_token"]
    if token_payload.get("refresh_token"):
        request.session["refresh_token"] = token_payload["refresh_token"]

    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request : Request, claims : dict = Depends(require_frontend_auth)):
    user_flw_reqs = user_follow_requests(claims.get("sub"))
    user_flwr_reqs = user_follower_requests(claims.get("sub"))
    friends = user_friends(claims.get("sub"))
    return templates.TemplateResponse(
            request=request, name="dashboard.html", context={"user" : claims.get("sub"),
                                                             "user_flw_reqs" : user_flw_reqs,
                                                             "user_flwr_reqs" : user_flwr_reqs,
                                                             "friends" : friends}
        )
