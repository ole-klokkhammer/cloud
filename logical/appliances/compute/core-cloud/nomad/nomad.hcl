# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: BUSL-1.1

# Full configuration options can be found at https://developer.hashicorp.com/nomad/docs/configuration


bind_addr  = "0.0.0.0"
name       = "core-cloud"
datacenter = "dc1"
data_dir   = "/opt/nomad/data"

client {
  enabled = true
  servers = ["control-plane.home.lan:4647"] # nomad server rpc address
  meta    = {
    role = "worker",
    machine  = "core",
    workload = "stateless"
  }
  # cni_path = "/usr/lib/cni"
  # cni_config_dir = "/etc/cni/net.d"
}

advertise {
  http = "core-cloud.home.lan:4646"
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