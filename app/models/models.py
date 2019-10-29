from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from app import db, bcrypt
from random import randint


_MIN = 1
_MAX = 1000000000


class User(db.Model):
    id = db.Column(db.BigInteger(), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))

    def __init__(self, first_name, last_name, email, password):
        self.id = randint(_MIN, _MAX)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = User.hashed_password(password)

    @staticmethod
    def create_user(payload):
        print("models.py: create_user(payload)")
        print(payload)
        user = User(
            email=payload["email"],
            password=payload["password"],
            first_name=payload["first_name"],
            last_name=payload["last_name"],
        )
        # print(user.id)
        # db.session.add(user)
        # print("models.py: added user")
        # db.session.commit()
        # print("models.py: committed")
        try:
            db.session.add(user)
            print("models.py: added user")
            db.session.commit()
            print("models.py: committed user to db")
            return True
        except IntegrityError:
            print("models.py: failed to commit user to db")
            return False

    @staticmethod
    def hashed_password(password):
        return bcrypt.generate_password_hash(password).decode("utf-8")

    @staticmethod
    def get_user_by_id(user_id):
        user = User.query.filter_by(id=user_id).first()
        return user

    @staticmethod
    def get_user_with_email_and_password(email, password):
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return None


class Task(db.Model):
    class STATUS:
        COMPLETED = "COMPLETED"
        IN_PROGRESS = "IN_PROGRESS"

    id = db.Column(db.BigInteger(), primary_key=True)
    date = db.Column(db.DateTime())
    task = db.Column(db.String(255))
    user_id = db.Column(db.String(255))
    status = db.Column(db.String(255))

    def __init__(self, task, user_id, status):
        self.id = randint(_MIN, _MAX)
        self.date = datetime.utcnow().date()
        self.task = task
        self.user_id = user_id
        self.status = status

    @staticmethod
    def add_task(task, user_id, status):
        print("models.py: add_task()")
        task = Task(task=task, user_id=user_id, status=status)
        print(task)
        db.session.add(task)
        print("models.py: added task")
        try:
            db.session.commit()
            print("models.py: committed addition of task_" + str(task.id))
            return True, task.id
        except IntegrityError:
            print("models.py: failed to add task--Integrity Error")
            return False, None

    @staticmethod
    def get_latest_tasks():
        print("models.py: get_latest_tasks()")
        user_to_task = {}

        result = db.engine.execute(
            """SELECT t.id, t.date, t.task, t.user_id, t.status, u.first_name, u.last_name
                from task t 
                INNER JOIN "user" u 
                    on t.user_id = u.email"""
        )  # join with users table

        print("result from db: ")
        print(result)
        for t in result:
            if t.user_id in user_to_task:
                user_to_task.get(t.user_id).append(dict(t))
            else:
                user_to_task[t.user_id] = [dict(t)]

        return user_to_task

    @staticmethod
    def get_tasks_for_user(user_id):
        print("models.py: get_tasks_for_user()")
        return Task.query.filter_by(user_id=user_id)

    @staticmethod
    def delete_task(task_id):
        task_to_delete = Task.query.filter_by(id=task_id).first()
        db.session.delete(task_to_delete)
        print("models.py: deleted task")

        try:
            db.session.commit()
            print("models.py: committed deletion")
            return True
        except IntegrityError:
            print("models.py: failed to delete")
            return False

    @staticmethod
    def edit_task(task_id, task, status):
        task_to_edit = Task.query.filter_by(id=task_id).first()
        task_to_edit.task = task
        task_to_edit.status = status

        print("models.py: edit_task ")
        print("task: " + task + " task_id: " + str(task_id))
        print("task_to_edit: " + str(task_to_edit))

        try:
            db.session.commit()
            print("models.py: commited edit")
            return True
        except IntegrityError:
            print("models.py: failed to commit edit")
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
