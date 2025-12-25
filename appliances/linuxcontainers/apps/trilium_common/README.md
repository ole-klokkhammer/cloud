# trilium common

## 
- lxc profile create trilium-common
- lxc profile edit trilium-common
- lxc launch ubuntu:24.04 trilium-common -p default -p trilium-common 
- if not existing on disk
  - download: https://docs.triliumnotes.org/user-guide/setup/server/installation/packaged-server
- copy systemd service and enable it