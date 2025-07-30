# backups

## setup
* curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
* unzip awscliv2.zip
* sudo ./aws/install
* set keys in profiles

## create profiles
* aws configure --profile etcd-backup
* aws configure --profile k3s-volume-backup

# allow running zfs backups with ubuntu user
* sudo zfs allow ubuntu snapshot,snapshot,send k3s

## monitoring
https://github.com/healthchecks/healthchecks
 