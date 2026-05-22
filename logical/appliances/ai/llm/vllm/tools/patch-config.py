#!/usr/bin/env python3
"""
Patch config.json of a vision-stripped Gemma 4 model to declare it as
a text-only model, so vLLM doesn't reserve VRAM for multimodal paths.
"""
import json
import shutil
import sys
from pathlib import Path

MODEL_DIR = Path("/models/gemma4/redhatai-31b-it-nvfp4-text-only")
CONFIG_PATH = MODEL_DIR / "config.json"

VISION_KEYS = {
    "vision_config",
    "vision_feature_layer",
    "vision_feature_select_strategy",
    "image_token_index",
    "audio_config",
    "audio_token_index",
    "video_token_index",
    "mm_tokens_per_image",
    "mm_tokens_per_audio",
    "mm_tokens_per_video",
}

# Backup
backup = CONFIG_PATH.with_suffix(".json.bak")
shutil.copy(CONFIG_PATH, backup)
print(f"Backed up to {backup}")

with open(CONFIG_PATH) as f:
    config = json.load(f)

# Patch architecture
original_arch = config.get("architectures")
config["architectures"] = ["Gemma4ForCausalLM"]
config["model_type"] = "gemma4"
print(f"Architecture: {original_arch} -> {config['architectures']}")

# Remove vision/audio/video keys
removed = []
for key in list(config.keys()):
    if key in VISION_KEYS:
        del config[key]
        removed.append(key)
if removed:
    print(f"Removed keys: {removed}")
else:
    print("No vision keys found to remove")

with open(CONFIG_PATH, "w") as f:
    json.dump(config, f, indent=2)

print("Done. Run vllm serve without --limit-mm-per-prompt flags.")
