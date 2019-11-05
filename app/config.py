import os


class BaseConfig(object):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(BaseConfig):
    COSMOS_DB_URI = "https://cosmosdb1029.documents.azure.com:443/"

    # not pushing keys to github
    SECRET_KEY = "" #key to cosmos
    AZURE_CLIENT_ID = "" 
    AZURE_TENANT_ID = ""
    AZURE_CLIENT_SECRET = ""
    DEBUG = True


class ProductionConfig(BaseConfig):
    COSMOS_DB_URI = os.environ.get("COSMOS_DB_URI", TestingConfig.COSMOS_DB_URI)

    # this is the key to cosmos db, but also used to make token for authentication purpose
    # probably shouldn't use the same key for different purposes and just let this key be the key to the db
    SECRET_KEY = os.environ.get("SECRET_KEY", TestingConfig.SECRET_KEY)
    
    # created an app service on Portal (b/c eventually want to use App Service to host app)
    # creds returned by making that app a service principal 
    # also, in order to use Identity, need a Service Principal 
    AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID", TestingConfig.AZURE_TENANT_ID)
    AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", TestingConfig.AZURE_CLIENT_ID)
    AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", TestingConfig.AZURE_CLIENT_SECRET)
    





