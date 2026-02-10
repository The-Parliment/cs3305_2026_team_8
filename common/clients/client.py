'''
This file represents the point where the client makes the call to the auth microservice.
This is still conceptually isolated from the auth microservice, frontend and backend are still separate.
The common/clients/ folder will have one file for each microservice to help make it easier to 
conceptualize how frontend and backend interact.
'''

import httpx

async def post(microservice_url: str, route: str, json: dict) -> dict | None:
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.post(f"{microservice_url}/{route}", json=json)
    if r.status_code == 401:
        return None
    r.raise_for_status()
    return r.json()