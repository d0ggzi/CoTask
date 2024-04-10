import random

import datetime
import fastapi
import fastapi.security as _security
from fastapi import Response

from src.database import db
import src.schemas as schemas
import jwt
from src.config import settings

oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="/api/token")


async def get_user_by_email(email: str) -> schemas.User | bool:
    try:
        db_id, db_email, fullname, position, color, team_name = db.get_user(email)
        user = schemas.User(id=db_id, email=db_email, fullname=fullname, position=position, color=color, team=team_name)
        return user
    except Exception as e:
        print(e)
        return False


async def create_user(user: schemas.UserCreate):
    team_id = db.get_team_by_name(user.team)
    if team_id == -1:
        raise fastapi.HTTPException(status_code=403, detail="No such team")
    random_color = "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
    user_id = db.reg_user(email=user.email, password=user.hashed_password, fullname=user.fullname,
                          position=user.position, color=random_color)
    db.create_user_team(user_id, team_id)

    user_res = schemas.User(id=user_id, email=user.email, fullname=user.fullname, position=user.position,
                            color=random_color, team=user.team)

    return user_res


async def authenticate_user(email: str, password: str) -> schemas.User | bool:
    user = await get_user_by_email(email)
    if not user:
        return False
    if not db.login(email, password):
        return False

    return user


async def create_token(user: schemas.User):
    token = jwt.encode(user.dict(), settings.JWT_SECRET)

    return dict(access_token=token, token_type="bearer")


async def get_current_user(token: str = fastapi.Depends(oauth2schema)) -> schemas.User:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user = await get_user_by_email(email=payload["email"])
        if not user:
            raise Exception("Bad credentials")
    except Exception as e:
        raise fastapi.HTTPException(status_code=401, detail="Could not validate credentials")

    return user


async def edit_user(user_edit: schemas.UserCreate, user: schemas.User):
    team_id = db.get_team_by_name(user_edit.team)
    if team_id == -1:
        raise fastapi.HTTPException(status_code=403, detail="No such team")

    random_color = db.edit_user(email=user_edit.email, password=user_edit.hashed_password, fullname=user_edit.fullname,
                           position=user_edit.position, user_id=user.id)
    old_team_id = db.get_team_by_name(user.team)
    db.delete_user_team(user.id, old_team_id)
    db.create_user_team(user.id, team_id)
    user_res = schemas.User(id=user.id, email=user_edit.email, fullname=user_edit.fullname, position=user_edit.position,
                            color=random_color, team=user_edit.team)

    return user_res


async def get_teams():
    return db.get_teams()


async def get_dashboards():
    return db.get_dashboards()


async def set_resp_for_task(task_id, user):
    if not db.user_is_resp_for_task(task_id, user.id):
        team_id = db.get_team_by_user_id(user.id)
        if not db.get_team_by_task_id(task_id) == team_id:
            raise fastapi.HTTPException(status_code=403, detail="User is in another team")
        db.set_resp_for_task(task_id, user.id)
        db.set_current_status_on_task(task_id, 'todo')
        return Response(status_code=200)
    else:
        raise fastapi.HTTPException(status_code=403, detail="User is already responsible for this task")


async def set_complete_percent_on_task(task_id, complete_percent, user):
    if db.user_is_resp_for_task(task_id, user.id):
        db.set_complete_percent_on_task(task_id, complete_percent)
        if complete_percent == 100:
            cur_datetime = datetime.datetime.now()
            db.set_fact_end_date(task_id, cur_datetime)
            db.set_current_status_on_task(task_id, 'finished')
        return Response(status_code=200)
    else:
        raise fastapi.HTTPException(status_code=403, detail="User is not responsible for this task")


async def set_current_status_on_task(task_id, current_status, user):
    team_id = db.get_team_by_user_id(user.id)
    if db.team_is_resp_for_task(task_id, team_id):
        if current_status == 'finished':
            db.set_complete_percent_on_task(task_id, 100)
            cur_datetime = datetime.datetime.now()
            db.set_fact_end_date(task_id, cur_datetime)
        db.set_current_status_on_task(task_id, current_status)
    else:
        raise fastapi.HTTPException(status_code=403, detail="User's team is not responsible for this task")


async def set_description_on_task(task_id, description, user):
    team_id = db.get_team_by_user_id(user.id)
    if db.team_is_resp_for_task(task_id, team_id):
        db.set_description_on_task(task_id, description)
    else:
        raise fastapi.HTTPException(status_code=403, detail="User's team is not responsible for this task")


async def get_dash_tasks(dash_name):
    tasks = []
    dash_id = db.get_dash_id_by_name(dash_name)
    tasks_from_db = db.get_dash_tasks(dash_id)

    for el in tasks_from_db:
        parents = [el[0] for el in db.get_parents(el[0])]

        users = []
        for resp in db.get_responsible_users_by_task(el[0]):
            user = schemas.User(id=resp[0], email=resp[1], fullname=resp[2], position=resp[3], color=resp[4],
                                team=resp[5])
            users.append(user)

        task = schemas.Task(id=el[0], name=el[1], current_status=el[2], complete_percent=el[3], description=el[4],
                            start_date=el[5], end_date=el[6], fact_end_date=el[7], duration=el[8], risk_level=el[9],
                            parents=parents, responsibles=users)
        tasks.append(task)

    return tasks


async def get_team_tasks(user: schemas.User):
    tasks = []

    team_id = db.get_team_by_user_id(user.id)
    tasks_from_db = db.get_team_tasks(team_id)

    for el in tasks_from_db:
        parents = [el[0] for el in db.get_parents(el[0])]

        users = []
        for resp in db.get_responsible_users_by_task(el[0]):
            user = schemas.User(id=resp[0], email=resp[1], fullname=resp[2], position=resp[3], color=resp[4],
                                team=resp[5])
            users.append(user)

        task = schemas.Task(id=el[0], name=el[1], current_status=el[2], complete_percent=el[3], description=el[4],
                            start_date=el[5], end_date=el[6], fact_end_date=el[7], duration=el[8], risk_level=el[9],
                            parents=parents, responsibles=users)
        tasks.append(task)

    return tasks


async def get_user_tasks(user: schemas.User):
    tasks = []

    tasks_from_db = db.get_user_tasks(user.id)

    for el in tasks_from_db:
        parents = [el[0] for el in db.get_parents(el[0])]

        users = []
        for resp in db.get_responsible_users_by_task(el[0]):
            user = schemas.User(id=resp[0], email=resp[1], fullname=resp[2], position=resp[3], color=resp[4],
                                team=resp[5])
            users.append(user)

        task = schemas.Task(id=el[0], name=el[1], current_status=el[2], complete_percent=el[3], description=el[4],
                            start_date=el[5], end_date=el[6], fact_end_date=el[7], duration=el[8], risk_level=el[9],
                            parents=parents, responsibles=users)
        tasks.append(task)

    return tasks
