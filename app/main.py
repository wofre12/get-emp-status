from contextlib import asynccontextmanager
from fastapi import FastAPI
from .data_access import DataAccess
from .settings import settings
from .api import router as emp_router
from .logger import DBLogger
from .bootstrap import init_database

data_access = DataAccess(settings.DATABASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database(data_access) 
    yield

app = FastAPI(title="GetEmpStatus Service", version="1.0.0", lifespan=lifespan)

# Wire router + logger
emp_router.data_access = data_access    
emp_router.db_logger = DBLogger(session_factory=data_access.get_session_factory(), enabled=settings.LOG_TO_DB)  
app.include_router(emp_router)

@app.get("/healthz")
async def healthz():
    return {"ok": True}
