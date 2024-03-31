import fastapi
import fastapi.security as _security
from fastapi import Security, BackgroundTasks
from src.utils.BackgroundProcessor import check_Tasks_deadlines
import src.services as _services, src.schemas as _schemas
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

app = fastapi.FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

allowed_users = {"admin@admin.com"}

scheduler = BackgroundScheduler()
scheduler.start()

background_tasks = BackgroundTasks()


def scheduled_tasks_check():
    check_Tasks_deadlines()


def execute_scheduled_task():
    background_tasks.add_task(scheduled_tasks_check())


scheduler.add_job(execute_scheduled_task, "interval", seconds=100)


def authenticate_user(user=Security(_services.get_current_user)):
    if user.email not in allowed_users:
        raise fastapi.HTTPException(status_code=401, detail="Недостаточно прав")
    return user


@app.post("/api/users")
async def create_user(
        user: _schemas.UserCreate
):
    db_user = await _services.get_user_by_email(user.email)
    if db_user:
        raise fastapi.HTTPException(status_code=400, detail="Email already in use")

    user = await _services.create_user(user)

    return user


@app.post("/api/token")
async def generate_token(
        form_data: _security.OAuth2PasswordRequestForm = fastapi.Depends(),
):
    user: _schemas.User = await _services.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    return await _services.create_token(user)


@app.get("/api/users/me", response_model=_schemas.User)
async def get_user(user=fastapi.Depends(_services.get_current_user)):
    return user


@app.get("/api/users/admin", response_model=_schemas.User)
async def get_user(user=fastapi.Depends(authenticate_user)):
    return user


@app.get("/api/data/roadmap", response_model=list[_schemas.Task])
async def get_roadmap(project_name: str, user=fastapi.Depends(_services.get_current_user)):
    return await _services.get_dash_tasks(project_name)


@app.get("/api/data/tasks", response_model=list[_schemas.Task])
async def get_tasks(user=fastapi.Depends(_services.get_current_user)):
    return await _services.get_team_tasks(user)


@app.post("/api/data/tasks")
async def set_resp_for_task(task_id: int, user=fastapi.Depends(_services.get_current_user)):
    return await _services.set_resp_for_task(task_id, user)


@app.put("/api/data/tasks")
async def set_complete_percent_for_task(task_id: int, complete_percent: int, user=fastapi.Depends(_services.get_current_user)):
    return await _services.set_complete_percent_on_task(task_id, complete_percent, user)


@app.get("/api/data/teams")
async def get_teams():
    return await _services.get_teams()


@app.get("/api/data/dashboards")
async def get_dashboards():
    return await _services.get_dashboards()

@app.get("/api/parse")
async def parse():
    from src.utils.excelParser import parseExcelTasks
    parseExcelTasks("./resources/Sample4.xlsx")
