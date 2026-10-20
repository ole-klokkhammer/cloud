# infernix

Wallawalla47/Infernix — CUDA 13 engine, serves OpenAI Chat/Responses + Anthropic
Messages APIs from `.infernix` artifacts. No public docker image to pull; build
from the bundled Dockerfile in the repo.

The llm LXC device is `nvidia.com/gpu=1` (host core, RTX 5090). Host
`/ssd/models/huggingface` binds to LXC `/models` (one dataset, one bind).

## setup

### build the image (llm LXC)
git clone https://github.com/Wallawalla47/Infernix
cd Infernix
podman build -t infernix .

Host NVIDIA driver >= 580 (CUDA 13) required; the image bundles the runtime.

### model (host core, one-off)
hf download wallawalla47/Qwen3.8-Flash-Next-NVIDIA-NVFP4-Dense8-Infernix \
  --local-dir /ssd/models/huggingface/qwen3.8/wallawalla47_Qwen3.8-Flash-Next-NVIDIA-NVFP4-Dense8-Infernix

~129 GB: 3 .infernix shards (~77 GB) + the 52 GB .ngram PLE volume
(any PLE volume runs every Flash-Next model). Re-running verifies/resumes
incomplete files.

### dflash2 drafter (same dir, ~776 MB)
hf download wallawalla47/Qwen3.8-Flash-Next-DFlash2-Infernix \
  Qwen3.8-Flash-Next-DFlash2-Infernix.infernix \
  --local-dir /ssd/models/huggingface/qwen3.8/wallawalla47_Qwen3.8-Flash-Next-NVIDIA-NVFP4-Dense8-Infernix

Block-diffusion drafer (drafter) used by `--spec dflash2` beside a main
artifact; one copy works with every Flash-Next artifact (FP8, NVFP4, IQ3_S...).

## run (llm LXC)

# /models already exists in the LXC (host bind) -> bind it into the container:
podman run --rm -it \
  --device nvidia.com/gpu=all \
  -p 8080:8080 \
  -v /models:/models:ro \
  infernix \
  infernix-serve /models/qwen3.8/wallawalla47_Qwen3.8-Flash-Next-NVIDIA-NVFP4-Dense8-Infernix/Qwen3.8-Flash-Next-NVIDIA-NVFP4-Dense8-Infernix-00001-of-00003.infernix \
    --ngram-volume /models/qwen3.8/wallawalla47_Qwen3.8-Flash-Next-NVIDIA-NVFP4-Dense8-Infernix/Qwen3.8-Flash-Next-NVIDIA-NVFP4-Infernix.ngram \
    --ngram-archive-mib 65536 \
    --host-context-mib 164000 \
    --ngram-native-sessions \
    --host 0.0.0.0 --port 8080 \
    --max-context 262144 \
    --kv-dtype fp8 \
    --prefill-chunk 4096 \
    --spec dflash2 \
    --draft-model /models/qwen3.8/wallawalla47_Qwen3.8-Flash-Next-NVIDIA-NVFP4-Dense8-Infernix/Qwen3.8-Flash-Next-DFlash2-Infernix.infernix \
    --draft-tokens auto \
    --lm-head-draft \
    --max-concurrency 2

`--spec dflash2 --draft-model` REPLACES `--spec mtp` (not both): the main
artifact's MTP drafter isn't loaded; the DFlash2 block-diffusion drafter proposes
up to 7 tokens per round instead.
`--draft-tokens auto` (recommended): drafts the 7-token block the drafter was
trained with, verifies only as many as worthwhile; fixed N was slower than MTP.
`--draft-model` needs a newer engine build: `infernix-serve --help` must list it
(`make update_push` here if not).
DFlash2 leaves ~330 expert-cache slots more than MTP on Dense8. The card
recommends fp8 KV (int8 also works; nvfp4 KV saves ~45% KV RAM; DFlash2 perf
was measured on int8).
Note: `--host-context-mib 164000` pins ~160 GiB; the llm LXD's cgroup cap is
128 GB, so the startup pin will fatal unless the LXC cap is raised.
Ctrl+C twice on stop saves the prefix cache.

## test

curl -s localhost:8080/v1/models                 # discover the model id
curl -s localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"<id-from-/v1/models>","messages":[{"role":"user","content":"Hello"}]}'

## make / service

Requires host podman + `lxc` and reachability to registry.linole.org; the
`Infernix/` clone sits next to the Makefile.

make update_push        # git pull the engine, podman build --pull (refreshes
# base images), podman push registry.linole.org/infernix:latest
make build_and_deploy   # update_push + push infernix.container into the llm LXC, restart
make restart | stop | status | logs

infernix.container runs the same flags as the run command above, persistently via
systemctl in the llm LXC (host-network, nvidia.com/gpu=all, /models ro).