# AI Appliances

This directory defines the logical AI services deployed across the GPU infrastructure. To maintain resource isolation and GPU pass-through stability, the services are split into two primary GPU-accelerated containers.

## Hardware Mapping

| Logical Appliance | Physical Hardware      | GPU Index | Primary Role      | Services Hosted                            |
| :---------------- | :--------------------- | :-------- | :---------------- | :----------------------------------------- |
| `llm`             | **RTX 5090**           | `gpu: 1`  | Core Generation   | Gemma 4 (31B)                              |
| `ai-utils`        | **RTX 5060 Ti (16GB)** | `gpu: 0`  | Support Pipeline  | Embeddings, Reranker, OCR, Music/Audio Gen |
| `agent`           | CPU / Shared           | N/A       | Logic & Execution | Hermes-Agent (Tool Coordination)           |

## Logical Architecture

### 1. `llm` (The Generator)

The primary inference engine. Dedicated to high-parameter models requiring maximum VRAM and compute.

- **Model:** Gemma 4
- **Focus:** Reasoning, generation, and complex instruction following.

### 2. `ai-utils` (The Senses & Pipeline)

A consolidated utility appliance hosting "helper" models that process inputs or generate specific media.

- **Context:** Embedding and Reranking models for RAG.
- **Vision:** OCR and Image Recognition models.
- **Audio:** Text-to-Audio / Music generation.
- **Role:** Pre-processing data for the LLM or post-processing LLM output into media.

### 3. `agent` (The Controller)

The orchestrator that connects the LLM to the actual system tools.

- **Engine:** Hermes-Agent
- **Role:** Manages tool-calling, executes scripts, and maintains state across the other AI appliances.
