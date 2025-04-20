# NextJS

* <https://nextjs.org/docs/app/getting-started/installation>
* <https://react.dev/blog/2025/02/14/sunsetting-create-react-app>

## setup next

* Install nodejs
* npx create-next-app@latest

## Azure test sandbox

* <https://learn.microsoft.com/en-us/training/modules/introduction-to-azure-app-service/5-authentication-authorization-app-service>

### upload

* az login --allow-no-subscriptions
* resourceGroup=$(az group list --query "[].{id:name}" -o tsv)
  appName=az204app$RANDOM
* az webapp up -g $resourceGroup -n $appName --html

### app settings

* az webapp config appsettings set -g $resourceGroup -n $appName --settings test1=value1 test2=value2
* <https://az204app30005.scm.azurewebsites.net/Env>

### Logs

* az webapp log tail --name appname --resource-group myResourceGroup
