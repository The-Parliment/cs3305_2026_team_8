import logging
from fastapi import FastAPI, HTTPException, Header, Depends

logging.basicConfig(level=logging.INFO, format='[events] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/proximity", title="proximity_service")

@app.get("/")
async def root():
    return {"message: Proximity Service API called"}

