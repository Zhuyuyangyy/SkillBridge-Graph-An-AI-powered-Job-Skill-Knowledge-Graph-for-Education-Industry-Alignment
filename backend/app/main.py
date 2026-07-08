from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.init_db import seed_database
from app.routers import graph_explore_router, router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    seed_database()
    yield


app = FastAPI(title="数融智联岗位能力图谱构建与分析系统", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "shurong-zhilian", "status": "running"}


app.include_router(router)
app.include_router(graph_explore_router)
