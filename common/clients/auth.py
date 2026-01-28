'''
This file represents the point where the client makes the call to the auth microservice.
This is still conceptually isolated from the auth microservice, frontend and backend are still separate.
The common/clients/ folder will have one file for each microservice to help make it easier to 
conceptualize how frontend and backend interact.
'''

import httpx

async def auth_login(auth_base_url: str, username: str, password: str) -> dict | None:
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.post(f"{auth_base_url}/login", json={"username": username, "password": password})
    if r.status_code == 401:
        return None
    r.raise_for_status()
    return r.json()