
bind_addr  = "0.0.0.0"
name       = "redis"
datacenter = "dc1"
data_dir   = "/opt/nomad/data"

client {
  enabled = true
  servers = ["nomad-server.home.lan:4647"] # nomad server rpc address
  meta    = {
    role = "redis",
    machine  = "core",
    workload = "stateless"
  }
  cni_path = "/usr/lib/cni"
  cni_config_dir = "/etc/cni/net.d"
}

advertise {
  http = "redis.home.lan:4646"
}

consul {
  enabled = true
  address = "http://consul-server.home.lan:8500"
  checks_use_advertise = true
}

plugin "nomad-driver-podman" {
  config {
    volumes {
      enabled      = false
    }
  } 
}