import time

from fastapi import BackgroundTasks, FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

scheduler = BackgroundScheduler()
scheduler.start()

background_tasks = BackgroundTasks()


def scheduled_tasks_check():#сюда пихаем проход по таскам и подсчет
    print('gavno')


def execute_scheduled_task():
    background_tasks.add_task()


scheduler.add_job(execute_scheduled_task, "interval", seconds=1)
while True:
    print('jopa')
    time.sleep(1)



