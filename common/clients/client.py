'''
This file represents the point where the client makes the call to the auth microservice.
This is still conceptually isolated from the auth microservice, frontend and backend are still separate.
The common/clients/ folder will have one file for each microservice to help make it easier to 
conceptualize how frontend and backend interact.
'''

import httpx

async def get(microservice_url: str, route: str, headers: dict | None=None, params: dict | None=None) -> dict | None:
    async with httpx.AsyncClient(timeout=5.0) as client:
        r: httpx.Response = await client.get(f"{microservice_url}/{route}", headers=headers, params=params)
    if r.status_code == 401:
        return None
    r.raise_for_status()
    return r.json()

async def post(microservice_url: str, route: str, headers: dict | None=None, json: dict | None=None, params: dict | None=None) -> dict | None:
    async with httpx.AsyncClient(timeout=5.0) as client:
        r: httpx.Response = await client.post(f"{microservice_url}/{route}", headers=headers, json=json, params=params)
    if r.status_code == 401:
        return None
    r.raise_for_status()
    return r.json()