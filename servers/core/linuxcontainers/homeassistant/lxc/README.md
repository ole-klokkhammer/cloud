# Homeassistant

## 
- lxc profile create homeassistant
- lxc profile edit homeassistant
- lxc launch ubuntu:24.04 homeassistant  -p default -p homeassistant
- bash
  - sudo useradd -rm homeassistant
  - sudo chown -R homeassistant:homeassistant /home/homeassistant
  - sudo chown -R homeassistant:homeassistant /config
  - sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update 
    sudo apt install python3.13-dev python3.13-venv python3-pip ffmpeg libturbojpeg
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1
    sudo update-alternatives --config python3
  - cd /home/homeassistant
    python3 -m venv homeassistant
    source homeassistant/bin/activate
    pip install --upgrade pip
    pip install wheel psycopg2-binary zlib-ng isal 
    pip install homeassistant 
  - cd /config
    sudo systemctl enable ./homeassistant.service
    sudo systemctl daemon-reload
    sudo systemctl enable homeassistant
    sudo systemctl start homeassistant


## upgrading 
source /home/homeassistant/homeassistant/bin/activate
pip install --upgrade homeassistant

