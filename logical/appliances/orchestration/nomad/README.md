# control-plane

Run the Nomad control plane in its own LXC and use a wildcard DNS plus Traefik pattern for browser-facing services.

The intended flow is:

1. pfSense resolves `*.nomad.home.lan` to the Traefik IP.
2. Traefik watches Nomad services.
3. Nomad jobs publish host rules for their service names.
4. A service like `matrix.nomad.home.lan` starts working without adding a new pfSense record.

This is an ingress pattern, not generic service discovery. It works well for HTTP and HTTPS apps exposed to users in a browser.

## storage

```bash
sudo zfs create -o compression=lz4 -o atime=off ssd/appdata/control-plane
sudo zfs set logbias=latency ssd/appdata/control-plane
```

## control-plane

- `lxc profile create control-plane`
- `lxc profile edit control-plane`
- `lxc launch ubuntu:24.04 control-plane -p default -p control-plane`
- `lxc exec control-plane -- bash`

## wildcard ingress model

### roles

- `pfSense`: resolves `*.nomad.home.lan` to Traefik.
- `Traefik`: terminates HTTP or HTTPS and routes by hostname.
- `Nomad`: schedules services and exposes metadata that Traefik consumes.

### naming convention

Use one hostname per browser-facing service:

- `matrix.nomad.home.lan`
- `plex.nomad.home.lan`
- `grafana.nomad.home.lan`

The convention should match the service name where practical. That keeps Traefik routing predictable and avoids extra DNS work.

### what becomes automatic

With a wildcard DNS record in pfSense, you do not need to create one DNS entry per service. A new app becomes reachable when both of these are true:

1. the hostname matches the wildcard, such as `app.nomad.home.lan`
2. Traefik has a router rule for that hostname and can forward traffic to the Nomad service

### what does not become automatic

- Traefik does not create DNS records in pfSense.
- This does not replace Consul-style service discovery for arbitrary TCP services.
- Non-HTTP services still need another discovery pattern or direct host and port usage.

## pfSense setup

This pattern assumes a stable Traefik IP or VIP on the LAN.

Create a wildcard DNS record in pfSense that points all Nomad app hostnames to Traefik:

- `*.nomad.home.lan -> <traefik-ip>`

Examples:

- `matrix.nomad.home.lan -> 192.168.x.y`
- `plex.nomad.home.lan -> 192.168.x.y`

Both resolve to the same Traefik address because Traefik, not pfSense, decides which backend gets the request.

For local DNS context and IP allocation ranges, see [physical/servers/pfsense/README.md](/home/ole/workspace/oleklokkhammer/projects/cloud/physical/servers/pfsense/README.md).

## Traefik plus Nomad routing

Traefik needs a Nomad-facing configuration so it can discover services and create host-based routes.

The important rule is simple:

- one Nomad service
- one hostname
- one Traefik router rule

The expected shape is:

```hcl
service {
	name     = "matrix"
	provider = "nomad"
	port     = "http"

	tags = [
		"traefik.enable=true",
		"traefik.http.routers.matrix.rule=Host(`matrix.nomad.home.lan`)",
		"traefik.http.services.matrix.loadbalancer.server.port=8008",
	]
}
```

Adjust the exact tag names if your Traefik Nomad integration uses a different provider or tag format. The principle stays the same: the Nomad job declares the hostname rule that Traefik should honor.

## end-to-end flow

When you deploy a new service:

1. you submit a Nomad job
2. the job exposes a service block with Traefik tags
3. Traefik discovers the service and registers the host rule
4. a client resolves `service.nomad.home.lan` through pfSense
5. pfSense returns the Traefik IP
6. Traefik inspects the Host header and forwards the request to the correct allocation

The only recurring per-service step is adding the Traefik rule in the Nomad job.

## validation

Use these checks after wiring the pattern up:

1. resolve a test hostname such as `matrix.nomad.home.lan` and confirm it returns the Traefik IP
2. open the hostname in a browser or curl it and confirm Traefik routes to the right service
3. deploy a second app such as `plex.nomad.home.lan` and confirm it works without adding a new pfSense record

## limitations

- This pattern is for user-facing HTTP or HTTPS services.
- It does not provide dynamic per-service records inside pfSense itself.
- It does not solve generic east-west service discovery inside the cluster.
- If you later need true service-discovery DNS, revisit Consul or another registry-backed DNS layer.
