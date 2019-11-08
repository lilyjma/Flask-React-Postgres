# Team Standup App  

This is a simple single page web app that integrates the Flask and React framework. It uses Track 2 versions of the [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python), specifically [azure-cosmos](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cosmos/azure-cosmos) and [azure-keyvault-secrets](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets), in addition to [azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity) for authentication purposes. 


The code is based on https://github.com/dternyak/React-Redux-Flask and https://github.com/creativetimofficial/material-dashboard-react.

## How to Run

## 1. Setting up Azure Services
First, sign up for a free [Azure](https://azure.microsoft.com/en-us/free/) account if you don't already have one. Sign into portal.azure.com.

[Create a resource group](https://github.com/lilyjma/azurethings/blob/master/createResourceGroup.md) to store the resources that you'll be using here--Azure Cosmos DB and Key vaults. Then follow the instructions in the links below to create the resources (remember to store them in the resource group you created): 

1. [Azure Cosmos DB](https://docs.microsoft.com/en-us/azure/cosmos-db/create-cosmosdb-resources-portal)
   1. When creating the database, name it 'team_standup'. For this app, you also need two containers named 'tasks' and 'users'. The [partition key](https://docs.microsoft.com/en-us/azure/cosmos-db/partitioning-overview#choose-partitionkey) for both is '/id'. 
2. [Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/quick-create-portal)
   1. This will store the credentials for the resources this app uses. For example, it'll store the key to the cosmos database. This way, you don't reveal any key in your code. 
   2. You'll add two secrets called 'cosmosKey' and 'cosmosURI' to Key Vault to hold the cosmos key and URI respectively. To find these, click into the Cosmos DB account created, go to 'Keys' tab and get the Primary Key and the URI. 

## 2. Getting Access to Key Vault
To make a long story short, you need a service principal to have access to key vault. The service principal serves as an application ID, which is used during the authorization setup for access to other Azure resources via RBAC (role-based access control). We'll use a Web App instance as our service principal. To do that, we create an App Service Plan, then a Web App instance, then make that our service principal on Cloud Shell (click >_ on the top right hand corner in Portal to open). 

1. Create App Service Plan : 
   
    ```az appservice plan create --name myServicePlanName --resource-group myResourceGroup --location westus```

    There are locations other than westus. A json object will pop up when the command is done. 

2. Create a Web App instance : (Note that the app name must be unique.)

    ```az webapp create --name myUniqueAppName --plan myServicePlanName --resource-group myResourceGroup```

3. Make the web app a service principal : 
    
    ```az ad sp create-for-rbac --name http://my-application --skip-assignment```

    Use your web app's url. To find that, click on the app in Portal, go to the 'Overview' tab and look for 'URL' on the top right portion of the page. It looks something like https://myUniqueAppName.azurewebsites.net. 

    After the above comand runs, something like this is returned: 
    ```
        {
           "appId": "11b855c6-43a5-415b-bd34-042a4509c179",
           "displayName": "myUniqueAppName.azurewebsites.net",
           "name": "https://myUniqueAppName.azurewebsites.net",
           "password": "5ad92c90-9e0b-4bcb-a3ad-a121e9076af1",
           "tenant": "72f998be-86f2-51ae-01af-2d5cd110db40"
        }
    ```

    Later you'll set environment variables, you'll need this info. The tenant will be saved as 'AZURE_TENANT_ID', appId as 'AZURE_CLIENT_ID', and password as 'AZURE_CLIENT_SECRET'. 

    

## 3. Setting Up The Project

1. Clone the reponsitory
   ```bash
   git clone https://github.com/lilyjma/Flask-React-Postgres/tree/team_standup_app_cosmos
   cd flask-react-postgres
   ```

2. Create and activate a virtual environment

   In Bash
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   In Powershell
   ```Powershell
   py -3 -m venv env
   env\scripts\activate
   ```

   In Powershell
   ```Powershell
   py -3 -m venv env
   env\scripts\activate
   ```

2. Install requirements.txt
   ```bash
   pip install -r requirements.txt
   ```

3. Import the project folder into VS Code
   ```bash
   code .
   ```

4. Create a .env file in the root directory
   1. Put these environment variables and their corresponding value in (you saved these in Step 2) : AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID, KEY_VAULT_URI. For example: 
   
        ```AZURE_CLIENT_ID="11b855c6-43a5-415b-bd34-042a4509c179"```

## 4. Running The Code Locally

1. Build the react.js front-end.
   ```
   npm install
   ```
    Go into the /static folder and do

    ```
    npm run build
    ```
    


2. Start the Flask server
   ```
   python manage.py runserver
   ```
4. Check ```localhost:5000``` in your browser to view the web application.

## 5. Deploying The Code To Azure

1. Go to the extensions tab on VS Code

2. Install the recommended extensions that show up (App Service Extension, Python Extension)

3. Reload the window and navigate to the Azure tab on the left

4. Access Azure services through (1) Guest Mode, (2) Creating a free Azure account or (3) signing into Azure with an existing account

5. Create an App Service instance with the parameters of a linux system with a Python runtime

6. Create a PostgreSQL database with Azure Database for Postgres and connect it to the App Service instance

7. Navigate to the Azure portal for the Azure Database for Postgres instance and allow incoming connections to the instance for everyone 

8. Navigate to the Azure portal for the App service instance that was just created, and under the "Application Settings" tab and uneder the "Runtime" section, set the "startup file" parameter to be "startup.txt"

9. Again under the "Application Settings" tab and under the "Application Settings" section, add a new environment variable for the Postgres 

10. Deploy the code to your newly created App Service instance

## License

Copyright (c) Microsoft Corporation. All rights reserved.

Licensed under the [MIT](LICENSE.txt) License.
