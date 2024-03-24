from RiskAlgorithm import TaskForAlgo
from excelParser import get_excel_tasks_dataset

def get_tasks_as_class(path:str):
    tasks = get_excel_tasks_dataset(path)
    return extract_tasks_to_class(tasks)

def extract_tasks_to_class(tasks: list[dict]):
    tasks_classes = list()

    for task in tasks:
        tasks_classes.append(TaskForAlgo(
            task.get("id"),
            task.get("name"),
            task.get("role"),
            task.get("start_date"),
            task.get("end_date"),
            task.get("duration"),
            task.get("parents")
        ))

    return tasks_classes
