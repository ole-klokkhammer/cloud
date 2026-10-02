\
# heynats - NATS web UI

Self-hosted [HeyNATS](https://github.com/astergaze-solutions/heynats) (React+Go, MIT).
Serves a browser UI on **:5000** of the host it runs on; you add your NATS server
as a connection inside the UI. The Go backend connects to NATS over plain TCP -
no NATS config changes, no WebSocket port needed.

## Layout

- `heynats.container` - podman quadlet (host network, port 5000, stateless)
- `Makefile` - runs on the **host** (core), like the detector's:
  `fetch` (git clone upstream into `src/heynats/`) -> `build` (podman) ->
  `push` (registry.linole.org) -> `deploy` (lxc file push quadlet + restart)
- `src/heynats/` - upstream checkout, **gitignored** (the repo is archived/frozen)

## First deploy (on the host, from this directory)

    make build_and_deploy
    make enable          # once

Then open `http://192.168.10.218:5000` (cameraagent LXC) and:

1. **New Connection** -> `nats://nats.homelan:4222`, no auth, save.
2. Subscribe tab -> subject `surveillance.detector` -> live burst messages.

Notes:
- Connections are kept in memory: after a container restart, re-add the connection.
- The server runs **JetStream off**, so the stream/consumer/KV panels are empty;
  the useful parts are live subject subscription, publish, connections and server stats.
- Repo is archived (frozen upstream) - treat as pinned; the image tag is the pin.
