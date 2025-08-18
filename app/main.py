from fastapi import FastAPI
from core import security, roles
from database.connection import Base, engine
from routes import job, candidate


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(security.router)
app.include_router(roles.router)
app.include_router(job.router)
app.include_router(candidate.router)

