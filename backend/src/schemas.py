import datetime as _dt
from typing import Optional

import pydantic as _pydantic


class _UserBase(_pydantic.BaseModel):
    email: str
    fullname: str
    position: str
    team: str


class UserCreate(_UserBase):
    hashed_password: str


class User(_UserBase):
    id: int
    color: str


class Dashboard(_pydantic.BaseModel):
    name: str


class Task(_pydantic.BaseModel):
    id: int
    name: str
    current_status: str
    complete_percent: int
    description: str
    start_date: _dt.datetime
    end_date: _dt.datetime
    fact_end_date: Optional[_dt.datetime] = None
    duration: float
    risk_level: int
    parents: list[int]
    responsibles: list[User]


class Team(_pydantic.BaseModel):
    name: str

