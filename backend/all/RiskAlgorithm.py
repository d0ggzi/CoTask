from datetime import datetime, timedelta


class TaskForAlgo:
    def __init__(self, id: int, name: str, role: str, start_date: datetime, end_date: datetime, duration, parents: list[int]):
        self.id = id
        self.name = name
        self.role = role
        self.start_date = start_date
        self.end_date = end_date
        self.duration = duration
        self.parents = parents
        self.risk_level = 0
        self.visited = False
        self.end_time = self.end_date

def process_tasks_deadline(tasks: list[TaskForAlgo]):
    tasks_dict = get_tasks_dict(tasks)
    for task in tasks:
        find_latest_time_for_cotask(task, tasks_dict)
    return tasks

def find_latest_time_for_cotask(task: TaskForAlgo, tasks_dict: dict[int, TaskForAlgo]):
    if task.visited:
        return
    latest_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    for index in task.parents:
        current_parent = tasks_dict[index]
        find_latest_time_for_cotask(current_parent, tasks_dict)
        latest_time = current_parent.end_time if latest_time < current_parent.end_time else latest_time
    task.visited = True
    task.end_time = latest_time + timedelta(days=(task.duration//8 + (task.duration % 8 > 0)))

    if task.end_date < task.end_time:
        task.risk_level = 2
    elif task.end_date < task.end_time + timedelta(days=2):
        task.risk_level = 1


def get_tasks_dict(tasks: list[TaskForAlgo]):
    tasks_dict = {}
    for task in tasks:
        tasks_dict[task.id] = task
    return tasks_dict


