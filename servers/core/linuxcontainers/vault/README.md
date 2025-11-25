# Hashicorp vault

## 
- lxc profile create vault
- lxc profile edit vault
- lxc launch ubuntu:24.04 vault -p default -p vault 
- lxc exec vault -- bash 
  - sudo apt update
    sudo apt install -y gnupg curl lsb-release

    # Add HashiCorp repo
    curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
    https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
    sudo tee /etc/apt/sources.list.d/hashicorp.list

    sudo apt update
    sudo apt install -y vault
  - ensure app data and config are set, then:
    sudo systemctl enable vault
    sudo systemctl start vault
    sudo systemctl status vault
- 


## permissions
# inside the vault LXC
sudo chown -R vault:vault /data/vault
sudo chmod -R u+rwX /data/vault