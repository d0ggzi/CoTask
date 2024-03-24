import random
import string

import pandas as pd
import json
from database import db


def parseExcelTasks(excelPath: str):
    df = pd.read_excel(excelPath, converters={"parents": parse_parents})

    df['start_date'] = df['start_date'].astype(str)
    df['end_date'] = df['end_date'].astype(str)

    data = df.to_dict(orient="records")
    id_to_obj = {item["id"]: item for item in data}

    name = excelPath.split("/")[-1].split('.')[0]
    rand_hash = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    dash_id = db.create_dashboard(name + rand_hash)
    indexes = dict()


    for item in data:
        #print(item)
        parents_str = item.get("parents", "")
        if parents_str:
            item["parents"] = [int(parent_id) for parent_id in parents_str.split(",")]

        # to database
        item["role"] = item["role"].strip()
        team_id = db.create_team(item["role"] + name + rand_hash, dash_id)
        task_id = db.create_task(item["name"], "", item["start_date"], item["end_date"], item["duration"])
        db.create_connection_task_team(team_id, task_id)
        db.create_connection_task_dash(dash_id, task_id)
        indexes[item["id"]] = task_id
    for item in data:
        cur_index = indexes[item["id"]]
        for parent in item["parents"]:
            if parent != 0:
                parent_index = indexes[parent]
                db.create_task_to_task(parent_index, cur_index)

        #to json
        item["children"] = [child_id for child_id, child in id_to_obj.items() if
                           str(item["id"]) in child.get("parents", [])]

    with open(f'../resources/{name}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def parse_parents(parents_str):
    parents_str = str(parents_str)
    if pd.isna(parents_str):  # Обрабатываем случай, если значение ячейки пустое
        return ""
    else:
        try:
            parent_ids = [int(parent_id.strip()) for parent_id in parents_str.split(",")]
            return ",".join(map(str, parent_ids))
        except ValueError:
            return ""


if __name__ == '__main__':
    parseExcelTasks("../resources/Sample1.xlsx")