node_name = "control-plane"
server           = true              # This node runs as a Consul server (not just an agent)
bootstrap_expect = 1                 # Expect 1 server in the cluster (set to 3 or 5 for HA)
datacenter       = "dc1"             # Logical datacenter name for grouping nodes
data_dir         = "/opt/consul"     # Where Consul stores its persistent state (Raft logs, KV, etc.)
client_addr      = "0.0.0.0"         # Listen on all interfaces for client (API, DNS, UI) requests

# bind_addr        = "0.0.0.0"         # Listen on all interfaces for cluster communication (RPC, gossip)
bind_addr = "{{ GetInterfaceIP \"eth0\" }}"
advertise_addr = "{{ GetInterfaceIP \"eth0\" }}"

ui_config {
  enabled = true
}