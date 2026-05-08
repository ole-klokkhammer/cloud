
bind_addr  = "0.0.0.0"
name       = "gpu-worker-0"
datacenter = "dc1"
data_dir   = "/opt/nomad/data"
plugin_dir = "/opt/nomad/plugins"

client {
  enabled = true
  servers = ["nomad.home.lan:4647"] # nomad server rpc address
  meta    = {
    role = "worker",
    machine  = "core",
    workload = "gpu"
  }
  # cni_path = "/usr/lib/cni"
  # cni_config_dir = "/etc/cni/net.d"

  host_volume "llama-models" {
    path      = "/home/ubuntu/llama-api/models"
    read_only = true
  }
}

# advertise {
#   http = "core-gpu.home.lan:4646"
# }

# consul {
#   enabled = true
#   address = "http://control-plane.home.lan:8500"
#   checks_use_advertise = true
# }

plugin "nomad-device-nvidia" {
  config {
    enabled = true
  }
}