
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
## prepare database
* sudo -u postgres psql -c "CREATE DATABASE k3s;"
* sudo -u postgres psql -c "CREATE USER k3s WITH PASSWORD <input from keystore>;"
* sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE k3s TO k3s;"
