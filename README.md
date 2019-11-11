# Team Standup App  

This is a simple single page web app that integrates the Flask and React framework. It uses Track 2 version of the [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python), specifically [azure-cosmos](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cosmos/azure-cosmos) and [azure-keyvault-secrets](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets), in addition to [azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity) for authentication purposes. 


The code is based on https://github.com/dternyak/React-Redux-Flask and https://github.com/creativetimofficial/material-dashboard-react.

## How to Run

## 1. Setting up Azure Services
First, sign up for a free [Azure](https://azure.microsoft.com/en-us/free/) account if you don't already have one. Sign into https://portal.azure.com.

[Create a resource group](https://github.com/lilyjma/azurethings/blob/master/createResourceGroup.md) to store the resources that you'll be using here--Azure Cosmos DB and Key Vault. Then follow instructions in the links below to create each resource in Azure Portal:

(Remember to store them in the resource group you created; this will make it easier to clean up the resources in the future.)

1. [Azure Cosmos DB](https://docs.microsoft.com/en-us/azure/cosmos-db/create-cosmosdb-resources-portal#create-an-azure-cosmos-db-account)
   1. When creating the database, give it an id of 'team_standup'. You also need two containers--give them id 'tasks' and 'users'. The [partition key](https://docs.microsoft.com/en-us/azure/cosmos-db/partitioning-overview#choose-partitionkey) for both is '/id'. 
2. [Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/quick-create-portal#create-a-vault)
   1. This will store credentials for the resources used by this app. For example, it'll store the key to the Cosmos DB. This way, you don't reveal any key in your code and have a centralized place for all keys the app uses. 
   2. You'll add two secrets called 'cosmosKey' and 'cosmosURI' to Key Vault to hold the Cosmos DB key and URI respectively. To find these, click into the database account created, go to 'Keys' tab and get the *Primary Key* and *URI*. 

You should be able to click into your resource group on the Azure Portal home page and see these two resources.

## 2. Getting Access to Key Vault
To make a long story short, you need a service principal to have access to Key Vault. The service principal serves as an application ID used during the authorization setup for access to other Azure resources. We'll use a Web App instance as our service principal. To do that, we create an App Service Plan, then a Web App instance, then make that our service principal and give it permission to perform operations to Key Vault. We can do these using Azure CLI on Cloud Shell. 


1. Click >_ on the top right hand corner of Azure Portal to open Cloud shell. 

2. Create App Service Plan : 
   
    ```az appservice plan create --name myServicePlanName --resource-group myResourceGroup --location westus```

    There are locations other than *westus*. A json object will pop up when the command is done. 

3. Create a Web App instance : (Note that the app name must be unique.)

    ```az webapp create --name myUniqueAppName --plan myServicePlanName --resource-group myResourceGroup```

    Find the web app instance you've just created on Azure Portal. In the 'Overview' tab, find *URL* on the top right portion of the page. This is your app's URL, and it looks something like this : https://myUniqueAppName.azurewebsites.net. Save it to use for the next step.

4. Make the web app a service principal : 
    
    ```az ad sp create-for-rbac --name https://myUniqueAppName.azurewebsites.net --skip-assignment```

    After ```--name``` , use your app's url.

    When the command finishes running, something like this is returned: 
    ```
        {
           "appId": "my-app-id",
           "displayName": "myUniqueAppName.azurewebsites.net",
           "name": "https://myUniqueAppName.azurewebsites.net",
           "password": "my-password",
           "tenant": "my-tenant"
        }
    ```

   Save this info in your favorite editor. In the next step, you'll set *appId* as an environment variable called AZURE_CLIENT_ID, and in a later step, you'll also set *tenant* as AZURE_TENANT_ID and *password* as AZURE_CLIENT_SECRET. 

5. Authorize the service principal to perform operations in your key vault:

    ```
    export AZURE_CLIENT_ID="my-azure-client-id"
    ```

   ```
   az keyvault set-policy --name my-key-vault --spn $AZURE_CLIENT_ID --secret-permissions get set list delete backup recover restore purge
   ```
    

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

3. Install requirements.txt
   ```bash
   pip install -r requirements.txt
   ```

4. Open the project folder in VS Code
   ```bash
   code .
   ```

5. Change the .env.tmp file in the root directory to .env
   
   Put in the correct value for each environment variable (you got the values in Step 2) : AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID, KEY_VAULT_URI. 
   
    To get KEY_VAULT_URI from Azure Portal, go to the key vault you created, then to the 'Overview' tap and look for *DNS Name* on the top right portion of the page.

## 4. Running The Code Locally

1. Build the react.js front-end
   ```
   npm install
   ```
    Go into the /static folder and do

    ```
    npm run build
    ```
    


2. Change back to root directory and start the Flask server
   ```
   python manage.py runserver
   ```
3. Check ```localhost:5000``` in your browser to view the web application.

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
