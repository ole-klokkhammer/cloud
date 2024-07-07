# 
* arkade get faas-cli
* arkade install openfaas
* arkade info openfaas # to get username and password?
* kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo
* faas-cli template pull

# Create functions EXAMPLE
* faas-cli new --lang python3 sunshine-follower
* faas-cli publish -f sunshine-follower.yml --platforms linux/amd64
* faas-cli deploy -f ./sunshine-follower.yml

# login openfaas faas-cli
* faas-cli login -u admin -p <password> --gateway http://192.168.0.203:8080