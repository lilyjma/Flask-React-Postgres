import os


class BaseConfig(object):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(BaseConfig):
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    print("testingConfig")
    # SQLALCHEMY_DATABASE_URI = f"postgresql://{os.environ['DBUSER']}:{os.environ['DBPASS']}@{os.environ['DBHOST']}/{os.environ['DBNAME']}"
    SQLALCHEMY_DATABASE_URI = "https://cosmosdb1029.documents.azure.com:443/"
    DEBUG = True
    SECRET_KEY = "somekey"  # needed but don't know why


class ProductionConfig(BaseConfig):
    print("productionConfig")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", TestingConfig.SQLALCHEMY_DATABASE_URI
    )
    SECRET_KEY = os.environ.get("SECRET_KEY", TestingConfig.SECRET_KEY)

