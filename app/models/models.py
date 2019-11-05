from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from app import client, bcrypt
from random import randint
import json, time
from azure.cosmos import CosmosClient, PartitionKey


# for task id
_MIN = 1
_MAX = 1000000000

user_container_name = "users"
task_container_name = "tasks"
db_name = "team_standup"


# get container by walking down resource hierarchy
# client -> db -> container
db = client.get_database_client(db_name)
user_container = db.get_container_client(user_container_name)
task_container = db.get_container_client(task_container_name)


class User:
    def __init__(self, first_name, last_name, email, password):
        # self.id = str(randint(_MIN, _MAX))  # id must be a string for cosmos
        self.id = email
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

    @staticmethod
    def create_user(input):
        try:
            user = User(
                first_name=input["first_name"],
                last_name=input["last_name"],
                email=input["email"],
                password=input["password"],
            )

            user_container.upsert_item(
                {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "password": user.password,
                }
            )

            return True
        except IntegrityError:
            return False

    @staticmethod
    def hashed_password(password):
        return bcrypt.generate_password_hash(password).decode("utf-8")

    @staticmethod
    def get_user_by_id(user_id):
        query = "SELECT * FROM users u where u.id=" + user_id
        users = user_container.query_items(
            query=query, enable_cross_partition_query=True
        )
        user = list(users)[0]

        return user

    @staticmethod
    def get_user_by_email(user_email):
        query = "SELECT * FROM users u where u.email='" + user_email + "'"
        users = user_container.query_items(
            query=query, enable_cross_partition_query=True
        )
        user = list(users)[0]

        return user

    @staticmethod
    def get_user_with_email_and_password(email, password):

        query = (
            "SELECT * FROM users u where u.email='"
            + email
            + "'"
            + " and u.password='"
            + password
            + "'"
        )
        users = user_container.query_items(
            query=query, enable_cross_partition_query=True
        )

        if users:
            user = list(users)
            return user[0]
        else:
            return None


class Task:
    class STATUS:
        COMPLETED = "COMPLETED"
        IN_PROGRESS = "IN_PROGRESS"

    def __init__(self, task, user_id, status):
        self.id = str(randint(_MIN, _MAX))
        self.date = str(datetime.utcnow().date())
        self.task = task
        self.user_id = user_id
        self.status = status

    @staticmethod
    def add_task(task, user_id, status):
        try:
            task = Task(task=task, user_id=user_id, status=status)
            task_container.upsert_item(
                {
                    "id": task.id,
                    "date": task.date,
                    "task": task.task,
                    "user_id": task.user_id, #user_id is email here
                    "status": task.status,
                }
            )

            return True, task.id
        except IntegrityError:
            return False, None

    @staticmethod
    def get_latest_tasks():
        user_to_task = {}

        query = "SELECT * FROM users"
        users = user_container.query_items(
            query=query, enable_cross_partition_query=True
        )

        cnt = 0
        for u in users:
            cnt+=1 
            task_query = "SELECT * FROM tasks t where t.user_id='" + u["id"] + "'"
            tasks = task_container.query_items(
                query=task_query, enable_cross_partition_query=True
            )
            for t in tasks:
                t["first_name"] = u["first_name"]
                t["last_name"] = u["last_name"]
                if t["user_id"] in user_to_task:
                    user_to_task.get(t["user_id"]).append(t)
                else:
                    user_to_task[t["user_id"]] = [t]

        return user_to_task

    @staticmethod
    def get_tasks_for_user(user_id):
        query = "SELECT * FROM tasks t where t.user_id='" + user_id + "'"
        tasks = task_container.query_items(
            query=query, enable_cross_partition_query=True
        )
        return tasks

    @staticmethod
    def delete_task(task_id):
        try:
            query = "SELECT * FROM tasks t where t.id='" + task_id + "'"
            tasks = task_container.query_items(
                query=query, enable_cross_partition_query=True
            )
            task = list(tasks)[0]
            task_container.delete_item(task, partition_key=task_id)

            return True
        except IntegrityError:
            return False

    @staticmethod
    def edit_task(task_id, task, status):
        try:
            task_to_edit = task_container.read_item(task_id, partition_key=task_id)
            task_to_edit["task"] = task
            task_to_edit["status"] = status

            task_container.upsert_item(task_to_edit)

            return True
        except IntegrityError:
            return False

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d"),
            "task": self.task,
            "user_id": self.user_id,
            "status": self.status,
        }
