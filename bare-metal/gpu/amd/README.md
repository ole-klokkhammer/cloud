# amd
- https://www.amd.com/en/developer/resources/technical-articles/running-llms-locally-on-amd-gpus-with-ollama.html
- https://rocm.docs.amd.com/projects/radeon/en/latest/docs/install/native_linux/install-radeon.html
- https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html
- https://markaicode.com/fix-rdna4-vulkan-performance-ubuntu-25-04/
- poor support for rocm on rx 470. use vulkan instead?!?
- 

## prereq
* sudo apt update && sudo apt upgrade -y
* sudo apt install linux-headers-generic build-essential dkms
* sudo apt install "linux-headers-$(uname -r)" "linux-modules-extra-$(uname -r)"
  
## support for ubuntu 25
https://www.omgubuntu.co.uk/2025/02/mesa-25-0-vulkan-1-4-amd-rdna4
* sudo add-apt-repository ppa:oibaf/graphics-drivers
* sudo apt update

=== Revert to original drivers ===
To revert to standard Ubuntu drivers type the following in a prompt shell:
$ sudo apt install ppa-purge
$ sudo ppa-purge ppa:oibaf/graphics-drivers

### vulkan now seems more optimized and MUCH easier to setup on amd gpus
* sudo apt update
* sudo apt install mesa-vulkan-drivers vulkan-tools radeontop 
* sudo update-initramfs -u
* sudo reboot
* radeontop

## ensure its not blacklisted
* sudo rm /etc/modprobe.d/blacklist-amdgpu.conf
 
## performance improvements
* sudo nano /etc/default/grub
* GRUB_CMDLINE_LINUX_DEFAULT="amdgpu.ppfeaturemask=0xffffffff amdgpu.dcfeaturemask=0x0 amdgpu.hw_i2c=1"
* sudo update-grub
* sudo reboot
