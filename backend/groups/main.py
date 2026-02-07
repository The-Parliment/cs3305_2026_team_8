import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format='[proximity] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/groups", title="groups_service")

@app.get("/")
async def root():
    return {"Groups Service: API called"}


