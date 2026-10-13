
from fastapi import FastAPI,HTTPException,Query,Depends,Request,Response
from pydantic import BaseModel,ConfigDict,Field,EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from models import Task,User
from security import hash_password, verify_password, create_access_token,get_current_user
import os
from fastapi.responses import JSONResponse

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from logging_config import configure_logging
import logging

app = FastAPI(title="LifeOS API")

configure_logging()
logger = logging.getLogger("lifeos")

#global exception handler
@app.exception_handler(Exception)
async def unexpected_error_handler(
    request: Request, exc: Exception
):
    logger.exception(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )



# configure rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded, _rate_limit_exceeded_handler
)



#health-check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str = None
class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    completed: bool

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    is_active: bool

#login request schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str

@app.get("/")
def home():
    return {"message": "LifeOS API is running!"}

#task creation end_point
@app.post("/tasks", status_code=201,response_model=TaskRead)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_task = Task(**task.model_dump(), owner_id=current_user.id)
    db.add(new_task)
    db.commit()
    logger.info("Task created: task_id=%s user_id=%s", new_task.id, current_user.id)
    db.refresh(new_task)
    return new_task

#list end_point
@app.get("/tasks",response_model=list[TaskRead])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    return (
        db.query(Task)
        .filter(Task.owner_id == current_user.id)
        .offset(skip).limit(limit).all()
    )

#get-task end_point
@app.get("/tasks/{task_id}",response_model=TaskRead)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id,
    ).first()
    if task is None:
        raise HTTPException(404, "Task not found")
    return task

#complete task end_point
@app.patch("/tasks/{task_id}/complete",response_model=TaskRead)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(
        Task.id == task_id, Task.owner_id == current_user.id
    ).first()
    if task is None:
        raise HTTPException(404, "Task not found")
    task.completed = True
    db.commit()
    return task

#update task end_point
@app.patch("/tasks/{task_id}",response_model=TaskRead)
def update_task(
    task_id: int, data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(
        Task.id == task_id, Task.owner_id == current_user.id
    ).first()
    if task is None:
        raise HTTPException(404, "Task not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    return task


# delete task end_point
@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(
        Task.id == task_id, Task.owner_id == current_user.id
    ).first()
    if task is None:
        raise HTTPException(404, "Task not found")
    db.delete(task)
    db.commit()

#registration end_point
@app.post("/auth/register", response_model=UserRead, status_code=201)
@limiter.limit("5/minute")
def register_user(request:Request,data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(409, "Email already registered")
    user = User(
        email=str(data.email),
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

#login end_point
@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request:Request,data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email == str(data.email)
    ).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid email or password")
    if not user.is_active:
        raise HTTPException(403, "Account is inactive")
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}

#gets current user
@app.get("/auth/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user

#database readiness end_point
@app.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception:
        return Response(
            content='{"status":"not_ready","database":"unavailable"}',
            status_code=503,
            media_type="application/json",
        )
