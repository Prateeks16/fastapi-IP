from fastapi import FastAPI
from core import security, roles
from database.connection import Base, engine
from routes import interview, question, sessions, answers, evaluation
from services import tasks


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(security.router)
app.include_router(roles.router)
app.include_router(interview.router)
app.include_router(question.router)
app.include_router(sessions.router)
app.include_router(answers.router)
app.include_router(evaluation.router)
app.include_router(tasks.router)


