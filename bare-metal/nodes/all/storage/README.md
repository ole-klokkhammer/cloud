# Storage

1. OS on two disk 1TB ZFS? Could maybe only use 500GB and attach the two to the hdd mirror for extra storage?
2. Two ssd disks in zfs mirror for fast storage, databases etc
3. Two 4 tb disks in zfs mirror for slower storage, music, pictures, surveillance
4. One big for torrents, movies, tv etc. Use ext4 for this

## questions
is hdd fast enough for k3s volumes?

## HOW TO

### ubuntu server disks 1 TB for growth 

1. **Boot Ubuntu Server Live ISO**  
   Choose "Try Ubuntu" or open a shell.

2. **Install ZFS tools**
   ```bash
   sudo apt update
   sudo apt install zfsutils-linux
   ```

3. **Partition both disks**  
   Replace `/dev/sda` and `/dev/sdb` with your disks.
   ```bash
   for disk in /dev/sda /dev/sdb; do
     sudo parted --script $disk \
       mklabel gpt \
       mkpart ESP fat32 1MiB 512MiB \
       set 1 boot on \
       mkpart primary 512MiB 100%
   done
   ```

4. **Format EFI partitions**
   ```bash
   sudo mkfs.fat -F32 /dev/sda1
   sudo mkfs.fat -F32 /dev/sdb1
   ```

5. **Create ZFS mirror pool**
   ```bash
   sudo zpool create -f -o ashift=12 \
     -O mountpoint=none \
     -O atime=off \
     -O compression=lz4 \
     rpool mirror /dev/sda2 /dev/sdb2
   ```

6. **Create ZFS datasets**
   ```bash
   sudo zfs create -o mountpoint=/ rpool/ROOT
   sudo zfs create -o mountpoint=/home rpool/HOME
   ```

7. **Mount and install Ubuntu**
   - Use debootstrap or the Ubuntu installer (with "Something Else" option) to install to `/mnt` (root on rpool/ROOT).
   - Mount EFI partitions:
     ```bash
     sudo mkdir -p /mnt/boot/efi
     sudo mount /dev/sda1 /mnt/boot/efi
     ```
   - (After install, copy EFI contents to `/dev/sdb1` as well.)

8. **Chroot and install GRUB on both disks**
   ```bash
   sudo mount --bind /dev /mnt/dev
   sudo mount --bind /proc /mnt/proc
   sudo mount --bind /sys /mnt/sys
   sudo chroot /mnt
   grub-install /dev/sda
   grub-install /dev/sdb
   update-grub
   exit
   ```

9. **Copy EFI boot files to second disk**
   ```bash
   sudo mount /dev/sdb1 /mnt/boot/efi2
   sudo cp -r /mnt/boot/efi/EFI /mnt/boot/efi2/
   sudo umount /mnt/boot/efi2
   ```

10. **Reboot and test failover**
    - Disconnect one disk, verify boot.
    - Reconnect, repeat for the other disk.


### Big disk for downloads, big data that need no redundancy
* sudo wipefs -a /dev/sdbX
* sudo mkfs.ext4 -F -L media /dev/sdX
* sudo mkdir -p /mnt/big
* sudo blkid /dev/sdX
* sudo mount UUID=e922a891-4878-434c-bc26-c2a37f7225b8 /mnt/big
* UUID="e922a891-4878-434c-bc26-c2a37f7225b8"  /mnt/big ext4  defaults  0  2
* sudo chown -R $USER:$USER /mnt/big


### HDD mirror 4TB for surveillance, music etc
* sudo zpool create hdd /dev/sdX
* sudo zfs create hdd/music
* sudo zfs create hdd/surveillance
* ...
* sudo zpool attach hdd /dev/sdX /dev/sdY
* sudo zpool status

### SSD mirror 1TB for databases and k3s volumes that needs speed
* sudo zpool create ssd /dev/sdX
* sudo zfs create ssd/postgres
* sudo zfs create ssd/k3s
* sudo zpool attach ssd /dev/sdX /dev/sdY
* sudo zpool status

## HOW TO MOUNT MANUALLY
mount disks with UUID for reliability

### MOUNTING
* sudo blkid
* sudo mkdir -p /mnt/databases
* sudo mount UUID=<your-uuid-here> /mnt/databases
* sudo nano /etc/fstab
* UUID=<your-uuid-here>  /mnt/databases  ext4  defaults  0  2
* sudo mount -a
 

## NFS provisioning
https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner?tab=readme-ov-file