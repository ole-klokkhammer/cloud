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