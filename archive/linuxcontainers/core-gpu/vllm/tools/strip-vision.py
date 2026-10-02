from safetensors.torch import load_file, save_file
import os, glob

input_dir = "/models/gemma4/redhatai-31b-it-nvfp4"
output_dir = "/models/gemma4/redhatai-31b-it-nvfp4-text-only"
os.makedirs(output_dir, exist_ok=True)

SKIP_PREFIXES = ("model.vision_tower.", "model.multi_modal_projector.")

for shard in sorted(glob.glob(f"{input_dir}/*.safetensors")):
    tensors = load_file(shard)
    filtered = {k: v for k, v in tensors.items()
                if not k.startswith(SKIP_PREFIXES)}
    if filtered:
        out_path = f"{output_dir}/{os.path.basename(shard)}"
        save_file(filtered, out_path)
        print(f"Saved {out_path} ({len(filtered)} tensors)")
    else:
        print(f"Skipped {shard} (all vision tensors)")


# then run this:
# cp /models/gemma4/nvidia-31b-it-nvfp4/{config.json,tokenizer*,*.json} /models/gemma4/nvidia-31b-it-nvfp4-text-only/
#