# opencode (npm: opencode-ai) as a browser service. `opencode web` serves the UI
# and the OpenAPI server on one port, so there is no separate frontend build.
# Also carries the pinned DuckDuckGo MCP server that opencode.json declares.
FROM docker.io/library/node:24-slim

# Pinned by the Makefile; opencode moves fast and the UI changes with it.
ARG OPENCODE_VERSION=1.19.5

RUN apt-get update \
 && apt-get install -y --no-install-recommends git ripgrep curl ca-certificates openssh-client \
      python3 python3-pip \
 && rm -rf /var/lib/apt/lists/*

# --allow-scripts is required, not cosmetic: npm 11 does not run install scripts
# by default and opencode-ai's postinstall is what fetches the platform binary.
# Without it the install "succeeds" and opencode is a stub, so assert next.
RUN npm install -g --allow-scripts=opencode-ai opencode-ai@${OPENCODE_VERSION} \
 && opencode --version

# The DuckDuckGo MCP is baked in rather than fetched by uvx on first use: the
# phone should not block on a PyPI resolution, and an unpinned resolve would let
# what the model is allowed to call drift between sessions. Debian is
# externally-managed (PEP 668), hence --break-system-packages (same as the
# detector image). Version must match the pin in opencode.json.
RUN pip install --no-cache-dir --break-system-packages "duckduckgo-mcp-server==0.7.0" \
 && command -v duckduckgo-mcp-server \
 && python3 -c "import importlib.metadata as m; print('duckduckgo-mcp-server', m.version('duckduckgo-mcp-server'))"

# node:24-slim already ships a uid 1000 user (`node`), so there is no useradd
# here - a second uid-1000 user fails the build. Reusing it also means checkouts
# in /workspace belong to the uid the agent runs as, so git sees no "dubious
# ownership"; the system-level safe.directory covers trees seeded by other uids.
RUN mkdir -p /workspace /home/node/.config/opencode \
 && chown -R node:node /workspace /home/node \
 && git config --system --add safe.directory '*'

# Both /workspace and /home/node back onto named volumes, and podman copies the
# image's ownership into a volume only when it first creates it - so the chown
# above has to stay, or a `make reset` leaves the agent unable to write its own
# sessions or model cache.
ENV HOME=/home/node \
    PYTHONUNBUFFERED=1

USER node
WORKDIR /workspace

# 0.0.0.0 is required, not convenience: opencode binds 127.0.0.1 by default and
# traefik lives in another netns on apps.network. Access control is the basic
# auth from EnvironmentFile plus VPN-only DNS, never the bind address.
EXPOSE 4096
CMD ["opencode", "web", "--hostname", "0.0.0.0", "--port", "4096"]
