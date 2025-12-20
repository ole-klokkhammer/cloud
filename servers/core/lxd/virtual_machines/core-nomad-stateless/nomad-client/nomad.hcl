
bind_addr  = "0.0.0.0"
name       = "core-nomad-stateless"
datacenter = "dc1"
data_dir   = "/opt/nomad/data"

client {
  enabled = true
  servers = ["nomad-server.home.lan:4647"] # nomad server rpc address
  meta    = {
    role = "worker",
    machine  = "core",
    workload = "stateless"
  }
}

advertise {
  http = "core-nomad-stateless.home.lan:4646"
}

consul {
  enabled = true
  address = "http://consul-server.home.lan:8500"
  checks_use_advertise = true
}

plugin "nomad-driver-podman" {
  config {
    volumes {
      enabled      = true
    }
  }
}