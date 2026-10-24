# mediamtx LXC



## Setup

```bash
lxc profile create mediamtx && lxc profile edit mediamtx   # paste profile.yaml
lxc launch ubuntu:24.04 mediamtx -p default -p mediamtx

make install-binary     # pinned VERSION (see Makefile); re-run with VERSION=x to upgrade
make deploy-unit
make start              # deploy-unit enables the unit but does not start it
```
## Verify

```bash
curl -s http://mediamtx.homelan:9997/v3/paths/list | head    # API
curl -s "http://mediamtx.homelan:9996/list?path=entrance_roof_sub" | head  # playback
ls -lt /hdd/surveillance/mediamtx/entrance_roof_sub/ | head   # fresh segments on host
```

## Cutover from the old surveillance-LXC quadlet

Only ONE ingest per camera at a time — cameras have few concurrent sessions:

```bash
# on the host, back-to-back (seconds of gap per stream):
lxc exec surveillance -- systemctl stop mediamtx
make start
```

Rollback is the inverse. Recordings are unaffected (same host path).

## Notes

- `mediamtx.yml` path chain comment still refers to the old quadlet mounts for
  the historical layout; the effective chain is now
  `host /hdd/surveillance/mediamtx -> LXC /media -> %path segments`.
- The detector republishes `entrance_roof_annotated` (publisher path) — it
  pushes here from the cloud LXC over RTSP.
