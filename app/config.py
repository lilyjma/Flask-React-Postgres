import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class BaseConfig(object):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(BaseConfig):
    # flaskreact app service as service principal
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
    KEY_VAULT_URL = os.getenv("KEY_VAULT_URL")

    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

    COSMOS_DB_URI = secret_client.get_secret("cosmosURI").value
    SECRET_KEY = secret_client.get_secret("cosmosKey").value  # key to cosmos

    DEBUG = True


class ProductionConfig(BaseConfig):
    # this is the key to cosmos db, but also used to make token for authentication purpose
    # probably shouldn't use the same key for different purposes and just let this key be the key to the db
    SECRET_KEY = TestingConfig.SECRET_KEY
    COSMOS_DB_URI = TestingConfig.COSMOS_DB_URI

    KEY_VAULT_URL = TestingConfig.KEY_VAULT_URL
    # created an app service on Portal (b/c eventually want to use App Service to host app)
    # creds returned by making that app a service principal
    # also, in order to use Identity, need a Service Principal
    AZURE_TENANT_ID = TestingConfig.AZURE_TENANT_ID
    AZURE_CLIENT_ID = TestingConfig.AZURE_CLIENT_ID
    AZURE_CLIENT_SECRET = TestingConfig.AZURE_CLIENT_SECRET

