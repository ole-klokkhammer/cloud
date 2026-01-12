# Coder
https://coder.com/

## setup
curl -L https://coder.com/install.sh | sh

To run a Coder server:

  # Start Coder now and on reboot
  $ sudo systemctl enable --now coder
  $ journalctl -u coder.service -b

  # Or just run the server directly
  $ coder server

  Configuring Coder: https://coder.com/docs/admin/setup

To connect to a Coder deployment:

  $ coder login <deployment url>