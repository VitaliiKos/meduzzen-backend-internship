from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from db.postgress_db import check_postgres_connection
from db.database import get_session
from db.redis_db import check_redis_connection

from config import settings

app = FastAPI()

origins = [
    settings.allow_host + ':' + str(settings.allow_port),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)


@app.get("/")
async def health_check():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


@app.get("/base_status")
async def base_status(session=Depends(get_session)):
    postgres_status = await check_postgres_connection()
    redis_status = await check_redis_connection()
    return {
        'postgres_status': postgres_status,
        'redis_status': redis_status
    }
