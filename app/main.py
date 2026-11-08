from fastapi import FastAPI

from app.api import tasks, users
from app.auth import router as auth_router

app = FastAPI(title="Task Tracker API", version="0.1.0")

app.include_router(auth_router.router)
app.include_router(users.router)
app.include_router(tasks.router)



@app.get("/")
def root():
    return {"service": "Task Tracker API", "docs": "/docs"}