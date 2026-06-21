import os
import time
from collections import defaultdict

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from routes import trips, destinations, users
from database.database import init_db

app = FastAPI(title="TripPilot AI API")
init_db()

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"null",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rate_limit_store = defaultdict(list)
RATE_LIMIT = {}


@app.middleware("http")
async def rate_limiter_middleware(request: Request, call_next):
    return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=()"
        return response


app.add_middleware(SecurityHeadersMiddleware)

app.include_router(trips.router)
app.include_router(destinations.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to TripPilot AI"}
