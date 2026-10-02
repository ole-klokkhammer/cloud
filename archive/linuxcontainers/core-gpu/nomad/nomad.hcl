
bind_addr  = "0.0.0.0"
name       = "core-gpu"
datacenter = "dc1"
data_dir   = "/opt/nomad/data"
plugin_dir = "/opt/nomad/plugins"

client {
  enabled = true
  servers = ["nomad.home.lan:4647"] # nomad server rpc address
  meta    = {
    role = "worker",
    machine  = "core",
    gpu  = "true"
  } 

  host_volume "llama-models" {
    path      = "/home/ubuntu/llama-api/models"
    read_only = true
  }
} 

plugin "nomad-device-nvidia" {
  config {
    enabled = true
  }
}