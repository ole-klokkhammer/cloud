# trilium ole

## 
- lxc profile create trilium-ole
- lxc profile edit trilium-ole
- lxc launch ubuntu:24.04 trilium-ole -p default -p trilium-ole 
- if not existing on disk
  - download: https://docs.triliumnotes.org/user-guide/setup/server/installation/packaged-server
- copy systemd service and enable it

## upgrade
# Take a snapshot of a dataset (name with timestamp)
- zfs snapshot ssd/appdata/trilium@pre-upgrade-2025-12-13

- sudo systemctl stop trilium
- [wget ](https://docs.triliumnotes.org/user-guide/setup/server/installation/packaged-server)
- ...