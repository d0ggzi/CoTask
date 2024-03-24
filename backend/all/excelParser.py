import pandas as pd
import openpyxl
import json

def get_tasks_df(excel_path: str):
    return pd.read_excel(excel_path, converters={"parents": parse_parents})


def get_excel_tasks_dataset(excel_path: str):
    df = get_tasks_df(excel_path)

    data = df.to_dict(orient="records")

    for item in data:
        parents_str = item.get("parents", "")
        if parents_str:
            item["parents"] = [int(parent_id) for parent_id in parents_str.split(",")]
            if item["parents"] == [0]:
                item["parents"] = []

    return data

def parseExcelTasks(excelPath: str):
    df = get_tasks_df(excelPath)

    df['start_date'] = df['start_date'].astype(str)
    df['end_date'] = df['end_date'].astype(str)

    data = df.to_dict(orient='records')

    id_to_obj = {item["id"]: item for item in data}

    for item in data:
        parents_str = item.get("parents", "")
        if parents_str:
            item["parents"] = [int(parent_id) for parent_id in parents_str.split(",")]
            if item["parents"] == [0]:
                item["parents"] = []

        item["children"] = [child_id for child_id, child in id_to_obj.items() if str(item["id"]) in child.get("parents", [])]

    json_data = json.dumps(data, indent=2, ensure_ascii=False)

    return json_data

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