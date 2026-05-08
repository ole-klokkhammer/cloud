name       = "nomad-server" # unique per server
datacenter = "dc1"
bind_addr  = "0.0.0.0"
data_dir   = "/opt/nomad/data"

server {
  enabled          = true
  bootstrap_expect = 1
}

client {
  enabled = false
}

ui {
  enabled = true
}

ports {
  http = 4646
  rpc = 4647
  serf = 4648
}

advertise {
 http = "nomad.home.lan:4646"
 rpc = "nomad.home.lan:4647"
 serf = "nomad.home.lan:4648"
}

# consul {
#   enabled = true
#   address = "http://nomad.home.lan:8500"
#   checks_use_advertise = true
# }

# vault {
#   enabled = true
#   address = "http://vault.home.lan:8200"
#   # token = "..."   # usually NOT hardcoded; use Nomad-Vault integration + policies
# }