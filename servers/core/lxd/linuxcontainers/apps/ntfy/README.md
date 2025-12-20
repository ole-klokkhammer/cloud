# ntfy

https://docs.ntfy.sh/install/

## setup 
- lxc profile create ntfy
- lxc profile edit ntfy
- lxc launch ubuntu:24.04 ntfy -p default -p ntfy
- lxc exec ntfy -- bash

sudo mkdir -p /etc/apt/keyrings
sudo curl -L -o /etc/apt/keyrings/ntfy.gpg https://archive.ntfy.sh/apt/keyring.gpg
sudo apt install apt-transport-https
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/ntfy.gpg] https://archive.ntfy.sh/apt stable main" \
    | sudo tee /etc/apt/sources.list.d/ntfy.list
sudo apt update
sudo apt install ntfy
sudo systemctl enable ntfy
sudo systemctl start ntfy