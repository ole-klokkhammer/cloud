
bind_addr  = "0.0.0.0"
name       = "gpu-worker-0"
datacenter = "dc1"
data_dir   = "/opt/nomad/data"

client {
  enabled = true
  servers = ["control-plane.home.lan:4647"] # nomad server rpc address
  meta    = {
    role = "worker",
    machine  = "core",
    workload = "gpu"
  }
  cni_path = "/usr/lib/cni"
  cni_config_dir = "/etc/cni/net.d"
}

advertise {
  http = "gpu-worker-0.home.lan:4646"
}

consul {
  enabled = true
  address = "http://control-plane.home.lan:8500"
  checks_use_advertise = true
}

vault {
  enabled = true
  address = "http://vault.home.lan:8200"
}