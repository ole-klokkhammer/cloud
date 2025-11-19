
# Setting up from scratch

## system services

1. setup metalb loadbalancer (https://metallb.universe.tf/installation/)
   * cd ./metalLB + follow readme 

2. add nginx ingress controller
    * cd ./nginx-ingress + follow readme
 
3. setup cert-manager
   * cd ./cert-manager + follow readme

4. setup dashboard
   * cd ./kubernetes-dashboard + follow readme
 
5. setup nvidia
   * cd ./nvidia + follow readme
 
6. setup longhorn
   * cd ./longhorn + follow readme

# external database
K3s uses the Postgres driver in Kine under the hood. When you point K3s at a Postgres endpoint, it actually:

Connects to the default postgres database to check whether your target database exists.

If needed, creates or migrates the target DB schema.

Continues operation against your configured database (e.g. k3sdb).

If your PostgreSQL setup denies that initial connect to postgres, K3s aborts with “permission denied.”

## do this
-- 1. Create the login role:
CREATE ROLE k3s WITH LOGIN PASSWORD 'XXXXX';

-- 2. Grant CONNECT on the system postgres DB:
GRANT CONNECT ON DATABASE postgres TO k3s;

-- 3. Create your actual K3s database:
CREATE DATABASE k3s OWNER k3s;

-- 4. (Optional) Fine-tune privileges:
GRANT ALL ON DATABASE k3s TO k3s;

## then allow pg_hba.conf
- sudo nano  /etc/postgresql/17/main/pg_hba.conf
- host    postgres,k3sdb    k3s    10.0.0.0/24    md5
- sudo systemctl reload postgresql
