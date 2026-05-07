sudo systemctl stop bluetooth
sudo systemctl disable bluetooth
sudo systemctl mask bluetooth

sudo apt install -y rfkill
sudo rfkill block bluetooth

sudo tee /etc/modprobe.d/blacklist-bluetooth.conf >/dev/null << 'EOF'
blacklist btusb
blacklist btrtl
blacklist btintel
blacklist btbcm
blacklist bluetooth
EOF
sudo update-initramfs -u

// reboot host
sudo reboot