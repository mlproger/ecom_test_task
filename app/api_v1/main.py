from contextlib import asynccontextmanager

import uvicorn
from app.api_v1.api import api_router as router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api_v1.settings.config import Config
from app.api_v1 import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db_pool()
    try:
        yield
    finally:
        await db.close_db_pool()

app = FastAPI(lifespan=lifespan) 
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)