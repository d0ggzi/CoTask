from MessageSender import send_message
from RiskAlgorithm import process_tasks_deadline
from RiskAlgorithm import TaskForAlgo
from database import db
import copy


def get_tasks_as_class():
    tasks = db.get_tasks()
    return extract_tasks_to_class(tasks)


def extract_tasks_to_class(tasks: list[dict]):
    tasks_classes = list()

    for task in tasks:
        tasks_classes.append(TaskForAlgo(
            id=task[0],
            name=task[1],
            start_date=task[5],
            end_date=task[6],
            duration=int(int(task[8]) * (1 - int(task[3]) / 100)),
            role=task[11],
            parents=[el[0] for el in db.get_parents(task[0])],
            risk_level=task[9]
        ))
    return tasks_classes


message = "Просим вас проверить cotask. Некоторые задания попали под риски срыва задач"


def send_broadcast_to_users(emails: list[str]):
    for email in emails:
        send_message(message, email)


def check_Tasks_deadlines():
    tasks_for_check = get_tasks_as_class()
    tasks = copy.deepcopy(tasks_for_check)
    process_tasks_deadline(tasks_for_check)
    check_if_changes(tasks, tasks_for_check)


def check_if_changes(init_tasks: list[TaskForAlgo], tasks: list[TaskForAlgo]):
    reports = {}
    for index, (init_task, task) in enumerate(zip(init_tasks, tasks)):
        if init_task.risk_level < task.risk_level:
            # запись в БД
            db.update_task(task.id, task.risk_level)
            if reports.get(task.role) is None:
                reports[task.role] = ""
            reports[task.role] += "По заданию " + task.name + " произошел сдвиг, который может повлиять на сроки\n"

    for (role, message) in reports.items():
        emails = db.get_email_by_team(role)  # users by role
        for email in emails:
            email = email[0]
            print(f"Sending message to {email}")
            send_message(message, email)
