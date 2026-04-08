# Torrent Stack

LXD container running Docker Compose with qBittorrent, Radarr, Sonarr, Lidarr, Jackett, Jellyseerr, and FlareSolverr behind ProtonVPN using WireGuard.

## Quick Start

```bash
make create          # create LXD container with profile
make install-docker  # install Docker + Compose plugin
make install-vpn     # install wireguard-tools + resolvconf
# push your WireGuard config into the container:
lxc file push wg0.conf core:torrent-stack/vpn/wg0.conf
make vpn-up          # bring up wg0, enable on boot
make vpn-killswitch-on  # iptables kill switch
make deploy          # push compose files + enable systemd service
```

Or: `make all` (create + configure + deploy).

## Operations

```bash
make status          # service + containers + WireGuard status
make logs            # tail docker compose logs
make restart         # restart the stack
make stop            # stop the stack
make shell           # shell into the container
make destroy         # destroy container (with confirmation)
```

## VPN

Uses WireGuard (`wg-quick`) inside the container with an iptables-based kill switch.

### WireGuard Config

Download a WireGuard config from ProtonVPN:

https://account.protonvpn.com/downloads

Pick **WireGuard**, choose a **P2P-capable server**, and save as `wg0.conf`.

Push it into the container:

```bash
lxc file push wg0.conf core:torrent-stack/vpn/wg0.conf
```

The config lives at `/vpn/wg0.conf` inside the container and is symlinked to `/etc/wireguard/wg0.conf` when `make vpn-up` runs.

### VPN Commands

```bash
make install-vpn        # install wireguard-tools, resolvconf, curl
make vpn-up             # bring up wg0 and enable on boot
make vpn-down           # bring down wg0 and disable boot service
make vpn-killswitch-on  # enable iptables kill switch
make vpn-killswitch-off # disable iptables kill switch
make vpn-status         # show wg interface + public IP
make configure-vpn      # install + up + status in one step
```

### Kill Switch

The kill switch uses iptables to set the OUTPUT policy to DROP, then only allows:

- loopback traffic
- traffic out the `wg0` interface
- LAN traffic to `192.168.10.0/24` via `eth0`
- the WireGuard endpoint IP via `eth0` (UDP, parsed from the config)
- IPv6 is fully blocked (OUTPUT DROP) except loopback and `wg0`

To enable or disable:

```bash
make vpn-killswitch-on
make vpn-killswitch-off
```

> **Note:** The kill switch rules are not persisted across reboots. Run `make vpn-killswitch-on` after a container restart, or add it to a boot script.

### Port Forwarding

ProtonVPN supports port forwarding via NAT-PMP on P2P servers. This allows inbound peer connections for better torrent performance.

For qBittorrent, enable **UPnP / NAT-PMP** in Settings → Connection.

### LXD Profile Requirements

The container profile needs these settings for WireGuard to work:

- `security.privileged: "true"`
- `security.nesting: "true"`
- `linux.kernel_modules:` must include `wireguard, udp_tunnel, ip6_udp_tunnel`
- `/dev/net/tun` exposed as a unix-char device
- `/lib/modules` mounted read-only for kernel module access

The host must have the WireGuard kernel modules loaded:

```bash
sudo modprobe wireguard udp_tunnel ip6_udp_tunnel
```

## Caveats

- WireGuard configs from ProtonVPN are tied to a specific server. To change servers, download a new config and push it again.
- The kill switch iptables rules do not persist across container restarts.
- If the WireGuard tunnel drops, all internet traffic is blocked until it reconnects (this is the intended kill switch behavior).
