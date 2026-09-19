# camagent LXC (core:camagent)

GPU LXC (RTX 5060 Ti, CDI passthrough) running the detection + query
stack as podman quadlets. Existing LXC: rename `core:surveillance` -> `core:camagent` (`pct set <id> hostname camagent` on PVE + DNS) so the name matches this folder.
mediamtx moved out to the mediamtx LXC, everything else stays here.

## services

| folder              | what                                                       | unit       |
|---------------------|------------------------------------------------------------|------------|
| `podman/detector/`  | YOLO11 cat detection, python/torch (CUDA): substream -> best-frame stills + NATS events | detector |
| `podman/embedder/`  | CLIP stills -> pgvector + NATS (the "ai-utils" role; LXC = camagent)       | embedder   |
| `podman/query/`     | camera query agent: POST /query, tools + LLM (on the 5090) | query      |
| `podman-registry/`  | in-LXC registry + login helper                              | -          |

NATS runs in its own LXC (`nats.homelan:4222`), not here.

## data flow

    camera -> mediamtx LXC (ingest + record + re-serve)
              -> detector: python/torch YOLO11 on the substream (CUDA) ->
                 per-burst best-frame stills (/detections/events) + one NATS event
                 (subject surveillance.detector, any consumer)

                 -> embedder: stills -> CLIP vectors -> postgres (pgvector) + NATS pub
                    -> query: NL question -> tools (postgres / embedder / mediamtx
                     playback / optional ai-utils vision) -> LLM (gemma on 5090) -> answer

the LLM never runs in this LXC: query calls the OpenAI-compatible
endpoint on the 5090 llm LXC. VRAM budget on the shared 5060 Ti:
YOLO ~1GB + CLIP ~1.5GB - leave headroom (the ai-utils LXC also shares
this card).

## storage (on core, shared with the mediamtx LXC)

    ssd/appdata/cameraagent      -> /config      (config/<svc> per service)
    hdd/surveillance/detections -> /detections  (detector writes stills to /detections/events;
                                                 embedder + query mount it :ro)
    ssd/llm/models/detector    -> /models (ro)   (the detector's .pt, shipped by 'make push-model')
    ssd/appdata/env            -> /env         (surveillance/<svc>.env secrets, never in git)

## setup (new build - the LXC likely already has these)

### podman

idempotent bootstrap (install + quadlet generator + auto-update timer + storage/registry checks):

    lxc exec core:camagent -- sh -c \
      'curl -fsSL <git>/logical/common/podman-setup.sh | bash'

(the same procedure inline, for reference):

sudo apt update && sudo apt install -y podman systemd-container gettext-base
systemctl enable --now podman-auto-update.timer

### nvidia container toolkit (CDI)

idempotent bootstrap for any GPU LXC (pinned, re-runnable, with smoke test):

    lxc exec core:camagent -- sh -c \
      'curl -fsSL <git>/logical/common/nvidia-cdi-setup.sh | bash'

(the block below is the same procedure inline, kept for reference)

https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/cdi-support.html

sudo apt-get update && sudo apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg2

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#' \
    | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update

export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.20.0-1
sudo apt-get install -y \
    nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}

sudo systemctl enable --now nvidia-cdi-refresh.path nvidia-cdi-refresh.service
sudo nvidia-ctk cdi generate --output=/var/run/cdi/nvidia.yaml
 
## deploy order

    sql:        psql -d postgres -f sql/schema.sql         (postgres LXC)
    nats:       (separate LXC - nats.homelan:4222; up before the detector starts)
    detector:   cd podman/detector && make push-model (core) && make image (LXC) && make deploy (core)
    embedder:   cd podman/embedder && make image (LXC) && make deploy (core)
    query:      cd podman/query && make image (LXC) && make deploy (core)

then: `lxc exec core:camagent -- systemctl enable detector embedder query`

## notes

- quadlets: /etc/containers/systemd/<svc>.container, deployed by each
  service's Makefile; images build inside the LXC and push to
  registry.linole.org
- detector details: podman/detector/README.md; per-service notes in each folder's README
- image names are fully qualified: the LXC's registries.conf has no
  unqualified-search registries
