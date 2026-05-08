# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: BUSL-1.1

# Full configuration options can be found at https://developer.hashicorp.com/nomad/docs/configuration


bind_addr  = "0.0.0.0"
name       = "core-cloud"
datacenter = "dc1"
data_dir   = "/opt/nomad/data"

client {
  enabled = true
  servers = ["nomad.home.lan:4647"] # nomad server rpc address
  meta    = {
    role = "worker",
    machine  = "core"
  }
}
