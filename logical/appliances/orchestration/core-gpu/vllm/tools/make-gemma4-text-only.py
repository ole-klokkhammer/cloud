#!/usr/bin/env python3
"""Convert a Gemma 4 multimodal checkpoint into a text-only checkpoint.

This copies non-weight assets, removes vision/audio/video tensors from the
weight shards, rewrites the safetensors index, and patches config.json so the
result can be served as a text-only model.
"""

from __future__ import annotations

import argparse
import glob
import json
import shutil
from pathlib import Path

from safetensors import safe_open
from safetensors.torch import save_file


DROP_PREFIXES = (
    "model.vision_tower.",
    "model.multi_modal_projector.",
    "model.embed_vision",
)

CONFIG_DROP_KEYS = {
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


def should_drop_tensor(name: str) -> bool:
    return name.startswith(DROP_PREFIXES)


def copy_metadata(input_dir: Path, output_dir: Path) -> None:
    for path in input_dir.iterdir():
        if path.suffix == ".safetensors":
            continue
        if path.name.endswith(".safetensors.index.json"):
            continue
        if path.is_file():
            shutil.copy2(path, output_dir / path.name)

    index_path = input_dir / "model.safetensors.index.json"
    if index_path.exists():
        shutil.copy2(index_path, output_dir / index_path.name)


def filter_shards(input_dir: Path, output_dir: Path) -> None:
    shard_paths = sorted(glob.glob(str(input_dir / "*.safetensors")))
    if not shard_paths:
        raise FileNotFoundError(f"No safetensors shards found in {input_dir}")

    for shard_path in shard_paths:
        shard = Path(shard_path)
        kept_tensors: dict[str, object] = {}
        removed_count = 0
        with safe_open(shard_path, framework="pt") as handle:
            for key in handle.keys():
                if should_drop_tensor(key):
                    removed_count += 1
                    continue
                kept_tensors[key] = handle.get_tensor(key)

        if not kept_tensors:
            continue

        save_file(kept_tensors, str(output_dir / shard.name))
        print(f"{shard.name}: kept {len(kept_tensors)} tensors, removed {removed_count}")


def patch_index(output_dir: Path) -> None:
    index_path = output_dir / "model.safetensors.index.json"
    if not index_path.exists():
        return

    with index_path.open() as fh:
        index = json.load(fh)

    weight_map = index.get("weight_map", {})
    removed = [name for name in weight_map if should_drop_tensor(name)]
    for name in removed:
        del weight_map[name]

    with index_path.open("w") as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")

    print(f"index: removed {len(removed)} multimodal tensor entries")


def patch_config(output_dir: Path) -> None:
    config_path = output_dir / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing config.json in {output_dir}")

    backup_path = output_dir / "config.json.bak"
    shutil.copy2(config_path, backup_path)

    with config_path.open() as fh:
        config = json.load(fh)

    config["architectures"] = ["Gemma4ForCausalLM"]
    config["model_type"] = "gemma4"

    removed_keys = []
    for key in list(config.keys()):
        if key in CONFIG_DROP_KEYS:
            del config[key]
            removed_keys.append(key)

    with config_path.open("w") as fh:
        json.dump(config, fh, indent=2)
        fh.write("\n")

    print(f"config: removed keys {removed_keys}")
    print(f"config: backup written to {backup_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    input_dir = args.input_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()

    output_dir.mkdir(parents=True, exist_ok=True)

    copy_metadata(input_dir, output_dir)
    filter_shards(input_dir, output_dir)
    patch_index(output_dir)
    patch_config(output_dir)

    print("done: serve the output directory as a text-only model")


if __name__ == "__main__":
    main()