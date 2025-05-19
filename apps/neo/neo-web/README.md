# neo-app

* npx shadcn@latest init
* ./deploy.sh patch

## kubernetes

* kubectl create secret generic neo-config --from-env-file=./src/.env -n neo
