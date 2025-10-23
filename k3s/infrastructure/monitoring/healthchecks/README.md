# healthchecks
https://github.com/healthchecks/healthchecks

## items
* etcd-backups on host
* postgres-backups on host


## setup
## database

-- Create a new database for healthchecks
CREATE DATABASE healthchecks;

-- set default db

-- Create a new user for healthchecks
CREATE USER healthchecks WITH PASSWORD '';

-- Grant privileges to the new user on the healthchecks database
GRANT ALL PRIVILEGES ON DATABASE healthchecks TO healthchecks;
GRANT USAGE ON SCHEMA public TO healthchecks;
GRANT CREATE ON SCHEMA public TO healthchecks;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO healthchecks;

## kubernetes
* kubectl create namespace healthchecks
* kubectl create secret generic -n monitoring  healthchecks-secrets --from-env-file=.env
* kubectl apply -f deployment.yaml
* enter pod, then:
    * manage.py migrate # create tables
    * manage.py createsuperuser
  
- id: '1750242115150'
  alias: Health checks Alert
  description: ''
  triggers:
  - trigger: webhook
    allowed_methods:
    - GET
    local_only: false
    webhook_id: healthchecks_alert
  conditions: []
  actions:
  - action: notify.mobile_app_pixel_5
    metadata: {}
    data:
      message: Hello
  mode: single


- id: '1750242368515'
  alias: Healthchecks Alert
  description: ''
  trigger:
    - platform: webhook
      webhook_id: healthchecks_alert
      allowed_methods:
        - POST
      local_only: false
  condition: []
  action:
    - type: toggle
      device_id: 89a954f5436d0c5be945030e4ad6164e
      entity_id: 0318953e61b4222f92ef70a2e2640cc9
      domain: light
  mode: single