# reolink
* https://github.com/mnpg/Reolink_api_documentations/blob/main/Bash-scripts/README.md#4-siren-activation--manual-mode-or-repeat-mode

* https://gist.github.com/jasonk/4772d1cd5154069cfc9eed07acb2057a

## curl
* Login:
  curl -k -s -H 'Content-Type: application/json'   -d '[{"cmd":"Login","action":0,"param":{"User":{"userName":"admin","password":"Gnxzsd7B"}}}]'   "http://192.168.10.110/cgi-bin/api.cgi?cmd=Login&token=null"
* 

## siren

* ./rl-api AudioAlarmPlay '{"alarm_mode": "manul", "manual_switch": 1, "channel": 0 }'
* ./rl-api AudioAlarmPlay '{"alarm_mode": "manul", "manual_switch": 0, "channel": 0 }'

## other commands
./rl-api GetDevInfo
./rl-api GetDevName
./rl-api GetTime
./rl-api GetAutoMaint
./rl-api GetHddInfo
./rl-api GetAutoUpgrade
./rl-api GetChannelStatus
./rl-api GetUser
./rl-api GetOnline
./rl-api GetLocalLink
./rl-api GetDdns
./rl-api GetEmail
./rl-api GetFtp
./rl-api GetNtp
./rl-api GetNetPort
./rl-api GetUpnp
./rl-api GetWifi