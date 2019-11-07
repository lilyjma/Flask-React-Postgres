from datetime import datetime, timedelta
from app import bcrypt
from random import randint
from app.utils.db import cosmosDB, exceptions
import json, time


# for task id
_MIN = 1
_MAX = 1000000000

# get container by walking down resource hierarchy
# client -> db -> container
user_container = cosmosDB.get_container_client("users")
task_container = cosmosDB.get_container_client("tasks")


class User():
    def __init__(self, first_name, last_name, email, password):
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
            user_container.create_item(user.__dict__)
            return True
        except exceptions.CosmosHttpResponseError:
            return False

    @staticmethod
    def hashed_password(password):
        return bcrypt.generate_password_hash(password).decode("utf-8")

    @staticmethod
    def get_user_by_id(user_id):
        users = user_container.query_items(
            query="SELECT * FROM users u WHERE u.id = @userId",
            parameters=[dict(name="@userId", value=user_id)],
            enable_cross_partition_query=True,
        )
        user = list(users)[0]

        return user

    @staticmethod
    def get_user_by_email(user_email):
        users = user_container.query_items(
            query="SELECT * FROM users u WHERE u.email = @userEmail",
            parameters=[dict(name="@userEmail", value=user_email)],
            enable_cross_partition_query=True,
        )
        user = list(users)[0]

        return user

    @staticmethod
    def get_user_with_email_and_password(email, password):
        users = user_container.query_items(
            query="SELECT * FROM users u WHERE u.email = @userEmail AND u.password = @userPassword",
            parameters=[
                dict(name="@userEmail", value=email),
                dict(name="@userPassword", value=password),
            ],
            enable_cross_partition_query=True,
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
            task_container.upsert_item(task.__dict__)
            return True, task.id
        except exceptions.CosmosHttpResponseError:
            return False, None

    @staticmethod
    def get_latest_tasks():
        user_to_task = {}

        users = user_container.query_items(
            query="SELECT * FROM users", enable_cross_partition_query=True
        )

        cnt = 0
        for u in users:
            cnt += 1
            tasks = task_container.query_items(
                query="SELECT * FROM tasks t WHERE t.user_id = @userId",
                parameters=[dict(name="@userId", value=u["id"])],
                enable_cross_partition_query=True,
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
        tasks = task_container.query_items(
            query="SELECT * FROM tasks t WHERE t.user_id = @userId",
            parameters=[dict(name="@userId", value=user_id)],
            enable_cross_partition_query=True,
        )
        return tasks

    @staticmethod
    def delete_task(task_id):
        try:
            tasks = task_container.query_items(
                query="SELECT * FROM tasks t WHERE t.id = @taskId",
                parameters=[dict(name="@taskId", value=task_id)],
                enable_cross_partition_query=True,
            )
            task = list(tasks)[0]
            task_container.delete_item(task, partition_key=task_id)

            return True
        except exceptions.CosmosHttpResponseError:  # item wasn't deleted successfully
            return False
        except exceptions.CosmosResourceNotFoundError:  # item wasn't found
            return False

    @staticmethod
    def edit_task(task_id, task, status):
        try:
            task_to_edit = task_container.read_item(task_id, partition_key=task_id)
            task_to_edit["task"] = task
            task_to_edit["status"] = status

            task_container.upsert_item(task_to_edit)

            return True
        except exceptions.CosmosHttpResponseError:  # item couldn't be upserted
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
