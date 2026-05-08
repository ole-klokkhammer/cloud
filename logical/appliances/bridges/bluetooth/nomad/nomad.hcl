
bind_addr  = "0.0.0.0"
name       = "hub0-bluetooth"
datacenter = "dc1"
data_dir   = "/opt/nomad/data"
plugin_dir = "/opt/nomad/plugins"

client {
  enabled = true
  servers = ["nomad.home.lan:4647"] # nomad server rpc address
  meta    = {
    role = "worker",
    machine  = "hub0",
    bluetooth  = "true"
  }
}

plugin "docker" {
  config {
    volumes {
      enabled = true
    }
  }
}
