#
- lxc profile create vault-agent
- lxc profile edit vault-agent
- lxc launch ubuntu:24.04 vault-agent -p default -p vault-agent
 

## setup
- install vault agent
  - # Add HashiCorp repo
    curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
    https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
    sudo tee /etc/apt/sources.list.d/hashicorp.list

    sudo apt update
    sudo apt install -y vault
- ensure token is set
  - echo 'VAULT_TOKEN=s.xxxxxxxx' | sudo tee /opt/vault/token.env
    sudo chmod 600 /opt/vault/token.env 
- 

## approle setup

auto_auth {
  method "approle" {
    mount_path = "auth/approle"
    config = {
      role_id_file_path   = "/opt/vault/role_id"
      secret_id_file_path = "/opt/vault/secret_id"
    }
  }

  sink "file" {
    config = {
      path = "/opt/vault/agent-token"
    }
  }
}