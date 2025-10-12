# policies

## Pre-mount hook for storage

* kubectl apply -f 
###  example use
```yaml
spec:
  template:
    metadata:
      annotations:
        storage.k8s.io/sentinel-check: "multi"
        storage.k8s.io/sentinel-volumes: |
          ["torrent-config","torrent-music-data","torrent-data"]
        # optional (default: .mounted)
        storage.k8s.io/sentinel-file: ".mounted"
    spec:
      # ensure these volumes are defined; the policy only injects an initContainer
      volumes:
        - name: torrent-config
          persistentVolumeClaim:
            claimName: torrent-config-pvc
        - name: torrent-music-data
          persistentVolumeClaim:
            claimName: torrent-music-pvc
        - name: torrent-data
          hostPath:
            path: /mnt/big/media
```