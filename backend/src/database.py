import random
from typing import Dict, Any, List, Tuple

import psycopg2
from src.config import settings
import bcrypt


def hash_password(password):
    password_bytes = password.encode("utf-8")
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt(12))
    return hashed_bytes.decode("utf-8")


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


class SQL:
    def __init__(self) -> None:
        self.conn = psycopg2.connect(
            f"""
            host={settings.POSTGRES_HOST}
            port={settings.POSTGRES_PORT}
            dbname={settings.POSTGRES_DB}
            user={settings.POSTGRES_USER}
            password={settings.POSTGRES_PASSWORD}
        """
        )
        self.cursor = self.conn.cursor()

    def get_user(self, email: str):
        with self.conn:
            self.cursor.execute(
                "SELECT id, email, fullname, position, color FROM users WHERE email=%s", (email,)
            )
            result = self.cursor.fetchall()
            if bool(len(result)):
                self.cursor.execute(
                    "SELECT name FROM teams t JOIN user_team o ON t.id = o.team_id WHERE o.user_id = %s", (result[0][0],)
                )
                team_name = self.cursor.fetchall()[0][0]
                return result[0][0], result[0][1], result[0][2], result[0][3], result[0][4], team_name   # found
        return True  # not found

    def reg_user(self, email: str, password: str, fullname: str, position: str) -> bool | int:
        password = hash_password(password)
        with self.conn:
            self.cursor.execute(
                "SELECT email FROM users WHERE email=%s", (email,)
            )
            result = self.cursor.fetchall()
            if not bool(len(result)):
                random_color = "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                self.cursor.execute(
                    "INSERT INTO users (email, password, fullname, position, color) VALUES (%s, %s, %s, %s, %s) "
                    "RETURNING id",
                    (email, password, fullname, position, random_color),
                )
                user_id = int(self.cursor.fetchall()[0][0])
                return user_id
        return False

    def get_team_by_name(self, team_name):
        with self.conn:
            self.cursor.execute(
                "SELECT id FROM teams WHERE name=%s", (team_name,)
            )
            result = int(self.cursor.fetchall()[0][0])
            return result

    def create_user_team(self, user_id, team_id):
        with self.conn:
            self.cursor.execute(
                "INSERT INTO user_team (user_id, team_id) VALUES (%s, %s)",
                (
                    user_id,
                    team_id
                ),
            )

    def login(self, email: str, password: str) -> bool | int:
        with self.conn:
            self.cursor.execute(
                "SELECT password, id FROM users WHERE email=%s", (email,)
            )
            result = self.cursor.fetchall()
            if bool(len(result)) and check_password(password, result[0][0]):
                return result[0][1]
        return False

    def create_team(self, team_name: str, dash_id) -> bool | int:
        with self.conn:
            self.cursor.execute(
                "SELECT id FROM teams WHERE name=%s", (team_name,)
            )
            result = self.cursor.fetchall()
            if not bool(len(result)):
                self.cursor.execute(
                    "INSERT INTO teams (name) VALUES (%s) RETURNING id",
                    (
                        team_name,
                    ),
                )
                team_id = int(self.cursor.fetchall()[0][0])
                db.create_connection_team_dashboard(team_id, dash_id)
                return team_id  # not found
            return int(result[0][0])  # found

    def create_dashboard(self, dashboard_name: str) -> bool | int:
        with self.conn:
            self.cursor.execute(
                "SELECT id FROM dashboards WHERE name=%s", (dashboard_name,)
            )
            result = self.cursor.fetchall()
            if not bool(len(result)):
                self.cursor.execute(
                    "INSERT INTO dashboards (name) VALUES (%s) RETURNING id",
                    (
                        dashboard_name,
                    ),
                )
                return int(self.cursor.fetchall()[0][0])  # not found
            return int(result[0][0])  # found

    def create_connection_team_dashboard(self, team_id, dashboard_id):
        self.cursor.execute(
            "INSERT INTO team_dashboards (team_id, dash_id) VALUES (%s, %s)",
            (
                team_id,
                dashboard_id
            ),
        )

    def create_task(self, task_name: str, description: str, start_date, end_date, duration) -> bool | int:
        with self.conn:
            self.cursor.execute(
                "INSERT INTO tasks (name, current_status, description, complete_percent, start_date, end_date, duration, risk_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (task_name, 'backlog', description, 0, start_date, end_date, duration, 0)
            )
            result = self.cursor.fetchall()

            return int(result[0][0])

    def create_connection_task_team(self, team_id, task_id):
        with self.conn:
            self.cursor.execute(
                "INSERT INTO task_team (task_id, team_id) VALUES (%s, %s)",
                (
                    task_id,
                    team_id
                ),
            )

    def create_connection_task_dash(self, dash_id, task_id):
        with self.conn:
            self.cursor.execute(
                "INSERT INTO task_dashboards (task_id, dash_id) VALUES (%s, %s)",
                (
                    task_id,
                    dash_id
                ),
            )

    def create_task_to_task(self, parent_id, child_id):
        with self.conn:
            self.cursor.execute(
                "INSERT INTO task_to_task (first_task_id, second_task_id) VALUES (%s, %s)",
                (
                    parent_id,
                    child_id
                ),
            )

    def get_team_by_user_id(self, user_id):
        with self.conn:
            self.cursor.execute(
                "SELECT team_id FROM user_team where user_id = %s", (user_id,)
            )
            team_id = int(self.cursor.fetchall()[0][0])
            return team_id


    def get_dash_id_by_name(self, dash_name):
        with self.conn:
            self.cursor.execute(
                "SELECT id FROM dashboards where name = %s", (dash_name,)
            )
            team_id = int(self.cursor.fetchall()[0][0])
            return team_id


    def set_resp_for_task(self, task_id, user_id):
        with self.conn:
            self.cursor.execute(
                "INSERT INTO user_task (task_id, user_id) VALUES (%s, %s)", (task_id, user_id)
            )


    def get_dash_tasks(self, dash_id):
        with self.conn:
            self.cursor.execute(
                "SELECT * FROM tasks t JOIN task_dashboards o ON t.id = o.task_id WHERE o.dash_id = %s", (dash_id,)
            )
            result = self.cursor.fetchall()
            return result

    def get_team_tasks(self, team_id):
        with self.conn:
            self.cursor.execute(
                "SELECT * FROM tasks t JOIN task_team o ON t.id = o.task_id WHERE o.team_id = %s", (team_id,)
            )
            result = self.cursor.fetchall()
            return result

    def get_teams(self):
        with self.conn:
            self.cursor.execute(
                "SELECT name FROM teams"
            )
            result = self.cursor.fetchall()
            return result

    def get_dashboards(self):
        with self.conn:
            self.cursor.execute(
                "SELECT name FROM dashboards"
            )
            result = self.cursor.fetchall()
            return result

    def get_tasks(self):
        with self.conn:
            self.cursor.execute(
                "SELECT * FROM tasks t JOIN task_team o ON t.id = o.task_id"
            )
            result = self.cursor.fetchall()
            return result

    def get_parents(self, task_id):
        with self.conn:
            self.cursor.execute(
                "SELECT first_task_id FROM task_to_task WHERE second_task_id = %s", (task_id,)
            )
            result = self.cursor.fetchall()
            return result

    def get_team_id_by_team_name(self, team_name):
        with self.conn:
            self.cursor.execute(
                "SELECT id FROM teams where name = %s", (team_name,)
            )
            team_id = int(self.cursor.fetchall()[0][0])
            return team_id

    def get_email_by_team(self, team_id):
        with self.conn:
            self.cursor.execute(
                "SELECT email FROM users u JOIN user_team t ON u.id = t.user_id WHERE team_id = %s", (team_id,)
            )
            result = self.cursor.fetchall()
            return result

    def update_task(
            self, task_id, task_risk_level
    ):
        with self.conn:
            self.cursor.execute(
                "UPDATE tasks SET risk_level = %s WHERE id=%s",
                (task_risk_level, task_id),
            )

    def get_responsible_users_by_task(self, task_id):
        with self.conn:
            self.cursor.execute(
                "SELECT u.id, email, fullname, position, color, teams.name FROM users u JOIN user_task t ON u.id = t.user_id JOIN user_team q ON u.id = q.user_id JOIN teams ON q.team_id = teams.id WHERE task_id = %s", (task_id,)
            )
            result = self.cursor.fetchall()
            return result

    def get_team_by_task_id(self, task_id):
        with self.conn:
            self.cursor.execute(
                "SELECT team_id FROM task_team where task_id = %s", (task_id,)
            )
            team_id = int(self.cursor.fetchall()[0][0])
            return team_id

    def user_is_resp_for_task(self, task_id, user_id):
        with self.conn:
            self.cursor.execute(
                "SELECT user_id FROM user_task WHERE user_id = %s AND task_id = %s", (user_id, task_id)
            )
            result = self.cursor.fetchall()
            if bool(len(result)):
                return True
        return False

    def set_complete_percent_on_task(self, task_id, complete_percent):
        with self.conn:
            self.cursor.execute(
                "UPDATE tasks SET complete_percent = %s WHERE id=%s",
                (complete_percent, task_id),
            )


    #
    # def get_task_lists(self, user_id: int) -> (bool, Dict[Any, Any]):
    #     with self.conn:
    #         task_lists = dict()
    #         self.cursor.execute(
    #             "SELECT name FROM task_lists WHERE owner_id=%s", (user_id,)
    #         )
    #         result = self.cursor.fetchall()
    #         for index, element in enumerate(result):
    #             task_lists[index] = element[0]
    #         return True, task_lists
    #
    # def update_task_list(
    #         self, task_list_old_name: str, task_list_new_name: str, user_id: int
    # ) -> (bool, str):
    #     with self.conn:
    #         self.cursor.execute(
    #             "SELECT id FROM task_lists WHERE name=%s and owner_id=%s",
    #             (
    #                 task_list_old_name,
    #                 user_id,
    #             ),
    #         )
    #         result = self.cursor.fetchall()
    #         if bool(len(result)):
    #             self.cursor.execute(
    #                 "UPDATE task_lists SET name=%s WHERE name=%s",
    #                 (task_list_new_name, task_list_old_name),
    #             )
    #             return True, task_list_new_name
    #     return False, "Task list with this name doesn't exists"
    #
    # def delete_task_list(self, task_list_name: str, user_id: int) -> (bool, str):
    #     with self.conn:
    #         self.cursor.execute(
    #             "SELECT id FROM task_lists WHERE name=%s and owner_id=%s",
    #             (
    #                 task_list_name,
    #                 user_id,
    #             ),
    #         )
    #         result = self.cursor.fetchall()
    #         if bool(len(result)):
    #             self.cursor.execute(
    #                 "DELETE FROM task_lists WHERE name=%s and owner_id=%s",
    #                 (task_list_name, user_id),
    #             )
    #             return True, "Successfully deleted task_list"
    #     return False, "Task list with this name doesn't exists"
    #
    # def check_task_list(self, task_list_name: str, user_id: int) -> int:
    #     with self.conn:
    #         self.cursor.execute(
    #             "SELECT id FROM task_lists WHERE name=%s and owner_id=%s",
    #             (
    #                 task_list_name,
    #                 user_id,
    #             ),
    #         )
    #         res = self.cursor.fetchall()
    #         if not bool(len(res)):
    #             return -1
    #         task_list_id = res[0][0]
    #         return task_list_id
    #
    # def create_task(
    #         self, task_list_name: str, task_name: str, description: str, user_id: int
    # ) -> (bool, str):
    #     task_list_id = self.check_task_list(task_list_name, user_id)
    #     if task_list_id == -1:
    #         return False, "No such task list"
    #     with self.conn:
    #         self.cursor.execute(
    #             "SELECT id FROM tasks WHERE name=%s and list_id=%s",
    #             (
    #                 task_name,
    #                 task_list_id,
    #             ),
    #         )
    #         result = self.cursor.fetchall()
    #         if not bool(len(result)):
    #             self.cursor.execute(
    #                 "INSERT INTO tasks (name, description, list_id) VALUES (%s, %s, %s)",
    #                 (
    #                     task_name,
    #                     description,
    #                     task_list_id,
    #                 ),
    #             )
    #             return True, "Task created successfully"
    #     return False, "Task with this name already exists"
    #
    # def get_tasks(self, task_list_name: str, user_id: int) -> (bool, List[Any]):
    #     task_list_id = self.check_task_list(task_list_name, user_id)
    #     if task_list_id == -1:
    #         return False, ["No such task list"]
    #     with self.conn:
    #         tasks = []
    #         self.cursor.execute(
    #             "SELECT name, description FROM tasks WHERE list_id=%s", (task_list_id,)
    #         )
    #         result = self.cursor.fetchall()
    #         for element in enumerate(result):
    #             curr_task = dict()
    #             curr_task["name"] = element[1][0]
    #             curr_task["description"] = element[1][1]
    #             tasks.append(curr_task)
    #         return True, tasks
    #
    # def update_task(
    #         self,
    #         task_old_name: str,
    #         task_new_name: str,
    #         new_desc: str,
    #         task_list_name: str,
    #         user_id: int,
    # ) -> (bool, str):
    #     task_list_id = self.check_task_list(task_list_name, user_id)
    #     if task_list_id == -1:
    #         return False, "No such task list"
    #     with self.conn:
    #         self.cursor.execute(
    #             "SELECT id FROM tasks WHERE list_id=%s and name=%s",
    #             (
    #                 task_list_id,
    #                 task_old_name,
    #             ),
    #         )
    #         result = self.cursor.fetchall()
    #         if bool(len(result)):
    #             self.cursor.execute(
    #                 "UPDATE tasks SET name=%s, description=%s WHERE list_id=%s and name=%s",
    #                 (
    #                     task_new_name,
    #                     new_desc,
    #                     task_list_id,
    #                     task_old_name,
    #                 ),
    #             )
    #             return True, task_new_name
    #     return False, "Task with this name doesn't exists"
    #
    # def delete_task(
    #         self, task_name: str, task_list_name: str, user_id: int
    # ) -> (bool, str):
    #     task_list_id = self.check_task_list(task_list_name, user_id)
    #     if task_list_id == -1:
    #         return False, "No such task list"
    #     with self.conn:
    #         self.cursor.execute(
    #             "SELECT id FROM tasks WHERE list_id=%s and name=%s",
    #             (
    #                 task_list_id,
    #                 task_name,
    #             ),
    #         )
    #         result = self.cursor.fetchall()
    #         if bool(len(result)):
    #             self.cursor.execute(
    #                 "DELETE FROM tasks WHERE list_id=%s and name=%s",
    #                 (
    #                     task_list_id,
    #                     task_name,
    #                 ),
    #             )
    #             return True, "Successfully deleted task"
    #         return False, "No such task"
    #
    # def is_admin(self, user_id: int) -> bool:
    #     with self.conn:
    #         self.cursor.execute(
    #             "SELECT roles.role FROM users JOIN roles ON users.role_id=roles.id "
    #             "WHERE users.id = %s",
    #             (user_id,),
    #         )
    #         result = self.cursor.fetchall()[0][0]
    #         return result == "admin"
    #
    # def admin_get_task_lists(self):
    #     with self.conn:
    #         task_lists = dict()
    #         self.cursor.execute(
    #             "SELECT task_lists.name FROM task_lists JOIN users "
    #             "ON task_lists.owner_id=users.id"
    #         )
    #         result = self.cursor.fetchall()
    #         for index, element in enumerate(result):
    #             task_lists[index] = element[0]
    #         return True, task_lists
    #
    # def admin_get_tasks(self, task_list_name: str) -> (bool, List[Any]):
    #     with self.conn:
    #         self.cursor.execute(
    #             "SELECT id FROM task_lists WHERE name=%s", (task_list_name,)
    #         )
    #         res = self.cursor.fetchall()
    #         if not bool(len(res)):
    #             return False, ["No such task"]
    #         task_list_id = res[0][0]
    #         tasks = []
    #         self.cursor.execute(
    #             "SELECT name, description FROM tasks WHERE list_id=%s", (task_list_id,)
    #         )
    #         result = self.cursor.fetchall()
    #         for element in enumerate(result):
    #             curr_task = dict()
    #             curr_task["name"] = element[1][0]
    #             curr_task["description"] = element[1][1]
    #             tasks.append(curr_task)
    #         return True, tasks


db = SQL()
