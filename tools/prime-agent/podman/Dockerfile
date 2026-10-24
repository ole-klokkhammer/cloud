FROM node:24

# Agent state dir; mounted as a named volume at runtime.
ENV PRIME_AGENT_CODING_AGENT_DIR=/home/agent/.prime/agent
RUN mkdir -p /home/agent/.prime/agent /workspace

# LLM provider config is NOT baked in: agent.sh bind-mounts podman/models.json
# (the repo copy) live at /home/agent/.prime/agent/models.json. Without that
# mount the container simply has no provider config until you register a
# workspace.
RUN curl -fsSL https://app.primeintellect.ai/prime-agent/install.sh | sh

# install.sh (run as root here) lands in /root/.local/bin and patches shell rc
# files, which `podman exec prime-agent` never sources. Put it on the ENV PATH.
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /workspace
