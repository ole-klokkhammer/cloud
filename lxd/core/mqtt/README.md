# MQTT broker (mosquitto, core:mqtt)

Single-broker MQTT for the fleet: the Ubuntu `mosquitto` package on its own LXC
(`core:mqtt`, Ubuntu 24.04, 1 CPU / 4 GB), reached by every client through traefik on
`core:cloud`. Replaces the NanoMQ container that ran as a quadlet on `core:cloud`.

```bash
make install           # apt install mosquitto + mosquitto-clients, restore packaged unit
make deploy            # state dirs + config + systemd drop-in, daemon-reload, restart
make config            # config only, then SIGHUP reload
make restart | status | logs
make test              # publish/subscribe on loopback and the LAN address
make save              # force a persistence write (SIGUSR1)
make uninstall         # stop, disable, drop the override (state kept)
```

Run it where `lxc` is configured for the `core:` remote:

```bash
make LXC_BIN='ssh core sudo lxc' deploy
```

## Layout

| in the instance                             | source in this directory  | contents                        |
| ------------------------------------------- | ------------------------- | ------------------------------- |
| `/ssd/appdata/mqtt/config/mosquitto.conf`   | `config/mosquitto.conf`   | broker config                   |
| `/ssd/appdata/mqtt/mosquitto/mosquitto.db`  | –                         | retained messages + QoS sessions |
| `/etc/systemd/system/mosquitto.service.d/fleet.conf` | `systemd/fleet.conf` | unit overrides            |

The config lives on the dataset rather than `/etc/mosquitto/` so a recreated instance
comes back with it and sanoid snapshots it, and so the deb's own config - which binds
loopback and denies anonymous - is never in play. The broker is started with
`-c /ssd/appdata/mqtt/config/mosquitto.conf` by the drop-in, and `make deploy` checks
the file is non-empty first: a missing config does not fail loudly, it falls back to
defaults.

State is the host's `ssd/appdata/mqtt` dataset via the `data` device in `profile.yaml`,
so it survives a recreated instance. It is mounted into `core:cloud` too, where the old
NanoMQ broker still holds `data/nano_qos_db.db` - which is why mosquitto's persistence
has its own `mosquitto/` directory instead of sharing `data/`.

`mosquitto.db` must be writable by the `mosquitto` user: the unit runs as `User=mosquitto`
and `ProtectSystem=strict` leaves only `ReadWritePaths` writable, so `make deploy`
creates the directory and chowns it.

## Not `/usr/lib/systemd/system/mosquitto.service`

Prefer a drop-in to editing the packaged unit. That file had been edited in place here
(`ExecStart` pointed at `/ssd/appdata/config/mosquitto.conf`, one `mqtt/` short of the
real mount point), so the broker had been running the deb config - loopback only, no
anonymous - while `systemctl status` looked healthy, and the next `apt upgrade` would
have reverted the edit anyway. Everything fleet-specific is in `systemd/fleet.conf`;
`make install`/`make upgrade` restore the packaged file when `dpkg --verify` reports it
modified.

The drop-in also clears `ExecStartPre`: the packaged lines `chown` `/var/log/mosquitto`
and `/run/mosquitto`, which fail once the unit runs as `User=mosquitto`, and neither
directory is used (logs go to stderr → journald, no `pid_file`).

Hardening is `User/Group=mosquitto` + `AmbientCapabilities=CAP_NET_BIND_SERVICE` (1883
is a privileged port) with an empty capability bounding set, `ProtectSystem=strict`,
`PrivateTmp`, `PrivateDevices`, `NoNewPrivileges`, `RestrictAddressFamilies=AF_INET
AF_INET6 AF_UNIX` (the last family is for `Type=notify`'s sd_notify socket) and
`RestrictNamespaces`.

## Config notes

`config/mosquitto.conf` documents each choice; the ones that bite:

- **`listener 1883 0.0.0.0`** - without a listener, mosquitto 2.x binds loopback only.
  Verify with `make deploy`, which prints the `ss` line: `0.0.0.0:1883`, not
  `127.0.0.1:1883`.
- **`allow_anonymous true`** - the fleet has always been open on the LAN, and 2.x
  defaults to refusing anonymous clients. Anyone who can reach 1883 can publish and
  subscribe; the file has the `password_file`/`acl_file` block to close it.
- **Unknown config variables are fatal** (`exit 3`, crash loop), so no option here is
  guessed - `tcp_nodelay` is documented in newer releases and absent from 2.0.18, which
  is what the first deploy crash-looped on. After an upgrade, `make logs` before
  believing a new option.
- **`persistence_location` and listeners are not reloadable** - `make config` sends
  SIGHUP, which covers auth, limits and logging; the rest needs `make restart`.

## Disk

```bash
sudo zfs create -o compression=lz4 -o atime=off -o xattr=sa -o acltype=posixacl \
  -o recordsize=1M ssd/appdata/mqtt
```

`recordsize=1M` is what the dataset was created with; the payload is SQLite pages, so
`4k` is the better fit, but at this volume it makes no difference.

## Instance

```bash
lxc profile create mqtt && lxc profile edit mqtt   # from profile.yaml
lxc launch ubuntu:24.04 mqtt -p default -p mqtt
make install && make deploy
```

## Path in

traefik publishes 1883 and its tcp service load-balances to this instance's LAN address
(see `../cloud/quadlets/containers/system/traefik/dynamic/mqtt.yaml`), so no client
changed when the broker moved:

| client | reaches |
| ------ | ------- |
| devices, off-instance | `cloud.homelan:1883` → traefik → `192.168.10.244:1883` |
| detector quadlet | `MQTT_HOST=mqtt.cloud.core.homelan` → same path |
| zigbee2mqtt (`core:zigbee`) | `mqtt://cloud.homelan:1883` → same path |

Two consequences worth knowing: every connection looks like it comes from traefik -
broker logs see traefik's address, not the device's, and mosquitto's listener has no
proxy-protocol option to get it back; and if traefik is down, no device can connect.
Publishing 1883 from `core:mqtt` itself and dropping the tcp router fixes both - then
clients must be repointed from `cloud.homelan` to the broker's address.

There is **no HTTP API or dashboard**: mosquitto 2.x ships neither. Watch
`make logs`, and query `$SYS/broker/#` with `mosquitto_sub -t '$SYS/broker/#'` (or
MQTTX from a workstation) for connected clients and throughput.

## Bring-up checks

```bash
make status && make logs        # "mosquitto version ... running", listener line
make test                       # prints `up` twice: loopback and LAN
make restart && make test       # still `up` = retained messages persisted
lxc exec core:mqtt -- ls -l /ssd/appdata/mqtt/mosquitto   # mosquitto.db, mosquitto:mosquitto
```

## Cutover from NanoMQ

The old broker may still be running on `core:cloud` (`lxc exec core:cloud -- podman ps
--filter name=mqtt`). Both sides can run at once - the container publishes nothing and
this broker binds only `core:mqtt`'s addresses - so bring mosquitto up, then cut over:

1. `make deploy && make test` here.
2. `make -C ../cloud/quadlets/containers/system/traefik deploy sync` - traefik picks up
   the new upstream and starts load-balancing to mosquitto.
3. Watch `make logs`: each client id should appear once, no reconnect loops.
4. Only then retire NanoMQ: `lxc exec core:cloud -- systemctl stop mqtt` and remove
   `/etc/containers/systemd/mqtt.container` + its `appdata_mqtt` device in
   `../cloud/profile.yaml`. Keep it a few days for rollback.

Retained messages do **not** migrate - neither NanoMQ's SQLite store nor mosquitto's
`mosquitto.db` can read the other's format. Home Assistant discovery and last-known
states republish when their publishers reconnect, but re-check the retained set:

```bash
lxc exec core:mqtt -- mosquitto_sub -t '#' -v -W 30
```

`$SYS/broker/retained messages/count` is not a shortcut here - mosquitto retains its own
~50 `$SYS` topics, so it reports that floor even on an empty broker.

Rollback: revert `dynamic/mqtt.yaml` to the `mqtt:1883` upstream, `make -C .../traefik
sync`, and `lxc exec core:cloud -- systemctl start mqtt`.