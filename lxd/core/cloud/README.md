# podman orchestration

## create vm

lxc profile create cloud
lxc profile edit cloud
lxc launch ubuntu:26.04 cloud -p default -p cloud
lxc exec cloud -- bash


## Surveillance services (moved from the surveillance LXC)

Quadlets live in [`podman/`](podman/) — detector, triton, embedder, query —
deployed with each dir's `make deploy` (target now `core:cloud`).

One-time prep in the cloud LXC:

```bash
lxc exec cloud -- mkdir -p /detector            # stills dir; detector writes, embedder/query read
# NATS must serve 127.0.0.1:4222 inside cloud (embedder/query expect it there).
```

Design notes:
- `/config`, `/env`, `/models` are the surveillance layout mounts from the
  profile — same host data, unchanged quadlet paths.
- **No `/media` mount on purpose:** recordings belong to the mediamtx LXC; the
  query agent fetches clips over its HTTP playback API (`QUERY_MEDIAMTX`), and
  the detector only speaks RTSP. Storage stays single-writer.
- GPU: triton + embedder expect the 5060 Ti — check the profile's gpu id.
