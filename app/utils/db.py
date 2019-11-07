from app import app
from azure.cosmos import CosmosClient


key = app.config["SECRET_KEY"]
uri = app.config["COSMOS_DB_URI"]

client = CosmosClient(uri, credential=key)

db_name = "team_standup"
cosmosDB = client.get_database_client(db_name)
