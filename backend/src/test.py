from src.utils.excelParser import parseExcelTasks
with open("/resources/Sample4.xlsx", "r") as file:
    parseExcelTasks(file)