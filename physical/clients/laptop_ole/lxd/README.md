# LXD

## install
install the static lxd client from the app store
sudo snap stop --disable lxd.daemon


## example remote deploy

// On the LXD host, expose the API
lxc config set core.https_address :8443
lxc config set core.trust_password <PASS>

// On your dev machine, add the remote
lxc remote add core core.homelan --password <PASS>
lxc remote add hub0 hub0.homelan --password <PASS>

// Use the remote prefix
lxc file push file.txt core:bluetooth/opt/app/
lxc exec hub0:bluetooth -- bash