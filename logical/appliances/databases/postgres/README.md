# postgres

## storage
sudo zfs create db/postgres
sudo zfs set atime=off db/postgres
sudo zfs set compression=lz4 db/postgres
sudo zfs set recordsize=8K db/postgres   # 8K–16K; see note below
sudo zfs set logbias=latency db/postgres
sudo zfs set primarycache=all db/postgres
sudo zfs set secondarycache=all db/postgres

Notes:

recordsize:
Postgres page size is 8K. For pure DB-only datasets, recordsize=8K aligns best.
16K is a decent compromise if you might also have larger files or want fewer metadata ops.
Pick one and keep it; changing it later only affects newly written blocks.
compression=lz4 is almost always a win for DBs (light CPU, saves IO).
atime=off avoids extra writes on reads.

## lxc
- lxc profile create postgres
- lxc profile edit postgres
- lxc launch ubuntu:24.04 postgres -p default -p postgres
- lxc exec postgres -- bash
 