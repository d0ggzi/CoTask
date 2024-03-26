import fastapi
import fastapi.security as _security

from database import db
import schemas
import jwt
from config import settings

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
    user_db = db.reg_user(email=user.email, password=user.hashed_password, fullname=user.fullname,
                          position=user.position)
    team_id = db.get_team_by_name(user.team)
    db.create_user_team(user_db, team_id)
    return user_db


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


async def get_teams():
    return db.get_teams()


async def get_dashboards():
    return db.get_dashboards()


async def get_dash_tasks(dash_name, user: schemas.User):
    tasks = []
    dash_id = db.get_dash_id_by_name(dash_name)
    tasks_from_db = db.get_dash_tasks(dash_id)

    for el in tasks_from_db:
        parents = [el[0] for el in db.get_parents(el[0])]
        task = schemas.Task(id=el[0], name=el[1], current_status=el[2], complete_percent=el[3], description=el[4],
                            start_date=el[5], end_date=el[6], fact_end_date=el[7], duration=el[8], risk_level=el[9],
                            parents=parents)
        tasks.append(task)

    return tasks


async def get_team_tasks(user: schemas.User):
    tasks = []

    team_id = db.get_team_by_user_id(user.id)
    tasks_from_db = db.get_team_tasks(team_id)

    for el in tasks_from_db:
        parents = [el[0] for el in db.get_parents(el[0])]
        task = schemas.Task(id=el[0], name=el[1], current_status=el[2], complete_percent=el[3], description=el[4],
                            start_date=el[5], end_date=el[6], fact_end_date=el[7], duration=el[8], risk_level=el[9],
                            parents=parents)
        tasks.append(task)

    return tasks
