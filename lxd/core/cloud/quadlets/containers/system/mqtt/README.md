# MQTT broker (NanoMQ, cloud LXC)

Single-broker MQTT for the fleet: NanoMQ as a podman quadlet in `core:cloud`,
alongside traefik, matrix, and the surveillance services. Replaces the HiveMQ CE
instance that used to live in its own LXC (`lxd/core/hivemq`).

```bash
make deploy            # state dirs + quadlet + config, restart
make config            # config only, restart
make restart
make status | logs
```

## Layout

| in the container               | host source                            | contents                        |
| ------------------------------ | -------------------------------------- | ------------------------------- |
| `/etc/nanomq.conf` (file, ro)  | `/ssd/appdata/mqtt/config/nanomq.conf` | broker config                   |
| `/var/lib/nanomq`              | `/ssd/appdata/mqtt/data`               | SQLite: retained + QoS sessions |
| `/tmp`                         | tmpfs                                  | entrypoint clears `nanomq.pid`  |

The config is bound as a **single file**, never as the config directory: NanoMQ
reads it from `/etc`, and a directory bind over `/etc` would hide the image's own
`/etc`. It also has to exist before the container is created - podman turns a
missing bind source into a directory, and the broker then cannot start - which is
what the `test -s` line in `make deploy` guards.

State is the host's `ssd/appdata/mqtt` dataset, bound in by the `appdata_mqtt`
disk device in the cloud profile (one device per service, like `appdata_traefik`
and `appdata_matrix` - there is no whole-`/ssd/appdata` mount), so it survives a
recreated instance.

No ownership arranging: the image runs as root and has no `USER` line, so the
SQLite directory only needs to be writable by root inside the container. Logs go
to stdout and from there to journald, so there is no log directory; `log { to =
[file, console] }` brings files back, into a directory that is then writable.

The image is named only in `mqtt.container` - no second copy in the Makefile, so
an upgrade is editing that `Image=` line plus `make deploy`.

## Image: `-slim`

Three variants exist per release; the plain tag is the basic one.

| variant | broker | TLS | SQLite | rule engine, QUIC bridge, bench |
| ------- | ------ | --- | ------ | ------------------------------- |
| `:0.25.7` | yes | no | **no** | no |
| `:0.25.7-slim` (used) | yes | yes | **yes** | no |
| `:0.25.7-full` | yes | yes | yes | yes |

`-slim` because without SQLite, retained messages and QoS 1/2 session state are
memory-only and gone on every restart. `-full` would add three things this broker
does not use. Note the official images are `emqx/nanomq`; the `nanomq/nanomq`
repository has not been published since 2022.

## Config

`config/nanomq.conf` starts from the file the image itself ships at
`/etc/nanomq.conf`. NanoMQ refuses keys it does not recognise and exits, so new
options get copied from the docs of the pinned version rather than guessed at.

Most changes do not need a restart: `nanomq reload --conf <file>` updates the
`basic`, `sqlite`, `auth` and `log` sections in place, e.g.

```bash
lxc exec core:cloud -- podman exec mqtt nanomq reload --conf /etc/nanomq.conf
```

## HTTP API, and the missing dashboard

NanoMQ has **no browser dashboard**, and `http_server` has no static-file option -
unlike mosquitto 2.1, which shipped one. `/` is a 404 and always will be, and the
v1 API is POST-only (`POST /api/v1`), so a browser cannot use that either. The v4
API is GET-based and is the surface worth using:

```
/api/v4/brokers   /api/v4/clients   /api/v4/subscriptions
/api/v4/metrics   /api/v4/prometheus   /api/v4/clients/{clientid}
```

```bash
curl -i -u admin:PASSWORD http://mqtt.cloud.core.homelan/api/v4/brokers
```

### Credentials

`auth_type = "basic"`, and NanoMQ 0.25.7 reads `username`/`password` **from the
config file only** - the config parser contains no `getenv`, so the
`NANOMQ_HTTP_SERVER_*` variables on the website's Docker page do nothing. Since
this config file is in git, the password is rendered in at container start:

1. `config/nanomq.conf` mounts read-only at `/etc/nanomq.tpl` and holds
   `password = "@API_PASSWORD@"`.
2. quadlet's `EnvironmentFile=` becomes podman's `--env-file` and loads
   `/ssd/appdata/env/nanomq.env`, which holds `NANOMQ_API_PASSWORD`.
3. The unit's `Exec` checks the variable is non-empty, `sed`s the placeholder into
   `/tmp/nanomq.conf` on tmpfs, then `exec`s `nanomq start --conf /tmp/nanomq.conf`.

The password therefore exists in one 0600 file on the instance and in tmpfs: never
in git, never on the dataset. An unset or empty variable fails the container rather
than starting a broker with a blank password. `make deploy` installs the env file
from `nanomq.env.example` once and never overwrites it.

Two things follow from rendering: the config the broker actually runs is
`/tmp/nanomq.conf`, so `nanomq reload --conf` must name that path (and reload only
covers `basic`, `sqlite`, `auth`, `log` - `http_server` needs a restart, which
`make config` does); and the password must avoid `|`, `&`, backslash, `$` and backtick,
because the render step is sed with a `|` delimiter inside a shell string.

For a real UI, use MQTTX against the broker, or a third-party web UI that speaks
MQTT; nothing on Docker Hub serves NanoMQ's API today.

## Disk

One dataset per service, as with matrix and traefik (sanoid snapshots
`ssd/appdata` recursively, so this is what gets backed up):

```bash
sudo zfs create -o compression=lz4 -o atime=off -o xattr=sa -o acltype=posixacl \
  -o recordsize=4k ssd/appdata/mqtt
```

`recordsize=4k`: the payload is SQLite pages and small appends, not large
sequential reads. The 128k default works too.

## Path in

The broker publishes no ports at all. Both listeners live on `apps.network`, and
traefik is the only way in - see `../traefik/dynamic/mqtt.yaml`.

| client | reaches | through |
| ------ | ------- | ------- |
| devices, other LXCs | `cloud.homelan:1883` | traefik `PublishPort=1883` -> tcp router -> `mqtt:1883` |
| on-instance containers | `mqtt:1883` | container DNS on `apps.network`, no traefik |
| API / curl | `http://mqtt.cloud.core.homelan` | traefik `web` -> http router -> `mqtt:8081`, basic auth |

| client | setting |
| ------ | ------- |
| detector quadlet | `Environment=MQTT_HOST=mqtt` |
| zigbee2mqtt (`core:zigbee`) | `mqtt: { server: mqtt://cloud.homelan:1883 }` |
| bluetooth bridges / bthome | `MQTT_BROKER=mqtt://cloud.homelan:1883` |

Off-instance clients keep using `cloud.homelan:1883`: traefik and the broker share
the cloud LXC's address, so moving the publish from one to the other changed nothing
for them.

Two consequences of routing MQTT through traefik:

- **traefik is now on the device path.** If it is down or being restarted, no device
  can connect. On-instance clients are unaffected.
- **Every connection looks like it comes from traefik.** Broker logs and any
  address-based rule see traefik's container address, and NanoMQ's listener config
  has no proxy-protocol option to get the device address back. If per-device
  addressing ever matters, the fix is publishing 1883 from the broker instead and
  dropping the tcp router.

## Deliberate choices

- **`allow_anonymous = true`.** Home LAN only, matching the old HiveMQ setup and the
  mosquitto config before it. Anyone on `apps.network`, plus anyone who can reach
  traefik's 1883, can publish and subscribe. Tightening it means
  `allow_anonymous = false` plus `auth { password = {include "/etc/nanomq_pwd.conf"}
  }` and an acl file - each of those needs its own single-file bind, and every
  device then needs credentials.
- **No MQTT-over-WebSocket listener** (`listeners.ws`, 8083). Nothing in the fleet
  uses one and traefik routes no path to it.
- **`ReadOnly=true`** works here - unlike the GPU quadlets, no CDI hooks write into
  the rootfs. `/tmp` is a tmpfs because the entrypoint deletes a pid file there.
- **TLS listener off.** Clients are on the LAN and behind traefik; the `-slim` image
  can do `listeners.ssl` on 8883 if a client ever leaves the LAN.

## Deploy order

1883 can only be published by one container at a time, so broker first, then proxy.
The reverse order fails to start traefik with "port is already allocated" and takes
the dashboard and every other route down with it.

```bash
make deploy                       # broker: no published ports
make -C ../traefik deploy sync    # traefik: gains 1883, picks up the route
```

Between the two, 1883 is unreachable from outside - a few seconds.

## Bring-up checks

```bash
lxc exec core:cloud -- podman ps --filter name=mqtt
lxc exec core:cloud -- podman logs --tail 30 mqtt
lxc exec core:cloud -- podman exec mqtt nanomq_cli pub -h 127.0.0.1 -t fleet/check -m up -r
lxc exec core:cloud -- podman exec mqtt nanomq_cli sub -h 127.0.0.1 -t fleet/check
```

`nanomq_cli` ships in the image; `sub` blocks until interrupted. The retained
publish is also the persistence check: after `make restart` the subscribe still
prints `up`, which is what the `-slim` image buys.

The broker crash-loops with `Restart=always` / `RestartSec=5`, so an unreadable or
invalid config shows up as a repeating journal rather than one clear failure. If the
config is there but the container cannot read it, test the bind on its own - this is
how the mosquitto attempt was narrowed down:

```bash
lxc exec core:cloud -- podman run --rm -v /ssd/appdata/mqtt/config:/c:ro \
  docker.io/emqx/nanomq:0.25.7-slim ls -l /c
```

## Cutover from HiveMQ

The repo copy of `lxd/core/hivemq` is gone. If the instance is still there
(`lxc info core:hivemq`), these steps apply; if it has been deleted, skip to the
client table above and just re-check the retained set.

HiveMQ and NanoMQ both want 1883, so they cannot run at once.

1. Deploy as above, then `make status` and `make logs` here.
2. Repoint the clients (table above), then redeploy each.
3. `make logs` - expect each client id once, no reconnect loops. Query the API.
4. Only then `lxc stop core:hivemq`; keep the instance for a few days.

Retained messages do NOT migrate - neither HiveMQ's nor mosquitto's persistence
format is readable by NanoMQ's SQLite store. Anything on a retained-only topic (HA
discovery, last-known states) republishes when its client reconnects, but re-check
the retained set after the switch. Rollback: `lxc start core:hivemq`, revert the
client env vars, and drop the mqtt entries from traefik again.

Left behind from the mosquitto attempt and safe to delete once NanoMQ is up:
`/ssd/appdata/mqtt/config/mosquitto.conf` and `/ssd/appdata/mqtt/log` on the
instance.
