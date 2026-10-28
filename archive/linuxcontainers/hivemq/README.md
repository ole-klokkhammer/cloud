# hivemq

HiveMQ Community Edition MQTT broker, running as a plain systemd service in the
`core:hivemq` LXC (no container runtime). See
[the CE configuration wiki](https://github.com/hivemq/hivemq-community-edition/wiki/Configuration)
and `config/config.xml` for broker settings (MQTT 1883, WebSocket 8000, file persistence).

## Layout

The Makefile only manages the broker inside the already-running instance — the
instance itself (LXD profile, launch) is managed separately through `profile.yaml`.
That profile bind-mounts the three state folders from the host, so they survive
reinstalls and a recreated instance:

| in the instance | host source                | contents                    |
| --------------- | -------------------------- | --------------------------- |
| `/config`       | `/ssd/appdata/hivemq/config`     | `config.xml`                |
| `/data`         | `/ssd/appdata/hivemq/data`       | persistence (file mode)     |
| `/extensions`   | `/ssd/appdata/hivemq/extensions` | extension dirs (auth etc.)  |

Releases live in `/opt/hivemq-ce/<version>` and `/opt/hivemq` is a symlink to the
active one, which is the path `config/hivemq.service` runs. Upgrades and rollbacks
are just a symlink flip.

## Deploy and operate

Everything goes through the Makefile (run it from a machine with the `lxc` CLI
configured for the `core:` remote); `make help` lists the targets.

```bash
make adopt              # one-time: move a pre-existing flat /opt/hivemq install
                        # into /opt/hivemq-ce/<version> and symlink it (make adopt FROM=2025.5
                        # if it cannot read the version from the journal)
make deploy             # JRE + unzip, hivemq user + folders, install VERSION,
                        # push config + unit, restart, check
make prereqs            # JRE and unzip only
make dirs               # hivemq service user and the /config /data /extensions mounts
make status             # unit state, active release, listening ports
make logs               # journal tail (make logs N=1000); make logs-f to follow
make errors             # recent warnings/errors only
make check              # unit + ports + extensions loaded + recent errors
make smoke              # publish/subscribe round trip inside the instance
make restart            # after any config.xml or extension change
make VERSION=2026.5 deploy    # upgrade to another release
make rollback TO=2025.5       # flip back and restart
make diff               # local config/config.xml vs the running one
make ext-builtin        # copy the extension bundled in the release into /extensions (no JDK)
make ext NAME=hivemq-allow-all-extension   # gradle build locally + push into /extensions
```

HiveMQ CE logs to stdout only (`conf/logback.xml` is console-based), so journald
is the log source: `journalctl -u hivemq.service -f`.

## Notes

- `config/hivemq.service` runs `bin/run.sh` as the `hivemq` user, which needs
  `/opt/hivemq` writable (heap dump + `log/` go to the home folder) — `make install`
  chowns it. `HIVEMQ_CONFIG_FOLDER`, `HIVEMQ_DATA_FOLDER` and `HIVEMQ_EXTENSION_FOLDER`
  point the broker at the mounted folders.
- `/data` must be writable by the `hivemq` user, or the broker logs
  `AccessDeniedException: /data/data.lock` and exits (with status 0, so systemd does
  not retry). That usually happens after HiveMQ was started by hand as root once — the
  lock file and persistence files stay root-owned. `make perms` fixes it; if it says
  the files are still not owned, `/data` is an idmapped mount (`shift: "true"`), so the
  `chown` has to run on the LXD host under `/ssd/appdata/hivemq/data` with the shifted
  uid from the `Uid map` in `lxc info core:hivemq`.
- HiveMQ looks for `logback.xml` next to `config.xml` (i.e. in `/config`), and warns on
  every boot if it is missing. `make config` seeds it from the release. The shipped
  config is console-only, which is what the default does anyway, so log output is
  unchanged either way.
- `make check` warns when `/extensions` is empty: with no auth extension, every
  client is rejected. `make ext-builtin` fixes that without a build by copying the
  allow-all extension that ships inside the release. `make ext` compiles the source
  under `extensions/` with `./gradlew` **on the machine running make**, so it needs a
  local JDK 17 (`sudo apt install openjdk-17-jdk-headless`) — use it only when you have
  changed the extension source.
- `bin/run.sh` enables JMX on port 9010 without authentication by default; it is
  reachable from the LAN unless the instance is firewalled.
- `make install` verifies the release before using it: `unzip -t` plus a
  `bin/hivemq.jar` size check (a full release is ~100 MB zipped, ~360 MB unpacked).
  A truncated `/tmp/hivemq-ce-<version>.zip` from an interrupted download is deleted
  on the spot — re-run to fetch it again.
- Manual install steps (what `make install` automates): install
  `openjdk-17-jre-headless`, unzip the release from
  [hivemq-community-edition releases](https://github.com/hivemq/hivemq-community-edition/releases)
  into `/opt/hivemq-ce/<version>`, symlink `/opt/hivemq` at it, chown to `hivemq`.
