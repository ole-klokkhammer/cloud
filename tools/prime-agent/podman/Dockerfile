FROM node:24

# Agent state dir; mounted as a named volume at runtime.
ENV PRIME_AGENT_CODING_AGENT_DIR=/home/agent/.prime/agent
RUN mkdir -p /home/agent/.prime/agent /workspace

# Bake the LLM provider config into the image (self-contained appliance).
COPY models.json /home/agent/.prime/agent/models.json

RUN curl -fsSL https://app.primeintellect.ai/prime-agent/install.sh | sh
 

WORKDIR /workspace
