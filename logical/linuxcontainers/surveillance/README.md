# surveillance

camera NVR stack, split across two LXCs + external services:

| folder                 | what                                          | where                    |
|------------------------|-----------------------------------------------|--------------------------|
| `mediamtx/`            | mediamtx: camera ingest, recording, playback  | `core:mediamtx` - unprivileged, CPU-only |
| `cameraagent/`         | detector (YOLO cat detection on the substream) + embedder + nats + query agent | `core:camagent` - 5060 Ti, GPU/CDI |
| `sql/`                 | postgres schema: events + pgvector            | `core:postgres` LXC      | 

## data flow

    camera -> mediamtx LXC (ingest + record + re-serve)
               -> camagent LXC:
                    detector  GPU YOLO cat events + stills (/detector/events)
                    embedder  stills -> CLIP vectors -> postgres (pgvector) + NATS
                    query     POST /query "how many cats today?"
                              -> tools (postgres / embedder / mediamtx playback /
                                 optional ai-utils vision) -> LLM (gemma on 5090) -> answer

## conventions

quadlets at /etc/containers/systemd/<name>.container, config in /config/<name>
(SSD pool), secrets in /env/surveillance/<name>.env (never in git).
still data: /detector (camagent, host HDD via LXD mount: /hdd/surveillance/detector);
recordings: /media/recordings (mediamtx LXC, host HDD via LXD mount: /hdd/surveillance).

see `mediamtx/README.md` and `cameraagent/README.md` for LXC setup.
