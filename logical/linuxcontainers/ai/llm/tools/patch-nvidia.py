from safetensors import safe_open
from safetensors.torch import save_file
import json, glob, torch

path = '/models/gemma4/nvidia-31b-it-nvfp4-text-only'
f = f'{path}/model-00004-of-00004.safetensors'

# Read all non-vision tensors
tensors = {}
with safe_open(f, framework='pt') as st:
    for key in st.keys():
        if not key.startswith('model.embed_vision'):
            tensors[key] = st.get_tensor(key)

print('Keeping:', len(tensors), 'tensors')
print('Sample keys:', list(tensors.keys())[:3])

# Rewrite file
import os; os.rename(f, f + '.bak')
save_file(tensors, f)
print('Done. Backup at', f + '.bak')

# Update index
idx_path = f'{path}/model.safetensors.index.json'
with open(idx_path) as fh:
    idx = json.load(fh)

removed = [k for k in idx['weight_map'] if k.startswith('model.embed_vision')]
for k in removed:
    del idx['weight_map'][k]
print('Removed from index:', len(removed), 'keys')

with open(idx_path, 'w') as fh:
    json.dump(idx, fh, indent=2)
print('Index updated')


# rm /models/gemma4/nvidia-31b-it-nvfp4-text-only/model-00004-of-00004.safetensors.bak