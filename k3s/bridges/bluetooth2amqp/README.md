# bluetooth
sudo apt install bluez

## setup
* kubectl create secret generic -n bridges  bluetooth2amqp-secrets --from-env-file=.env
* kubectl apply -f ./schedules.yaml
* kubectl create -f ./deployment.yaml 

## airthings
* https://github.com/Airthings/wave-reader/blob/master/read_wave.py
* https://github.com/Airthings/waveplus-reader/blob/master/read_waveplus.py

## xiaomi
* https://github.com/uduncanu/lywsd03mmc

## BLE parser
* https://github.com/hbldh/bleak
* https://pypi.org/project/bleparser/
* https://github.com/custom-components/ble_monitor
* https://bitbucket.org/bluetooth-SIG/public/src/main/assigned_numbers/