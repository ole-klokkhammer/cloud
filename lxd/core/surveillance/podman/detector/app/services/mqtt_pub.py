"""MQTT publisher for the detector service (HiveMQ at hivemq.homelan).

The MQTT counterpart of nats_pub.py: background, auto-reconnecting, and
*queues nothing lost*: paho's client runs its own network thread and
`publish()` is thread-safe, so the capture thread can publish without
ever blocking on the broker. Burst-only, like the NATS path - same
detection_burst payloads, QoS 0 (a missed broker = a missed event; the
still on disk is the source of truth).

Per-camera topics: the configured base topic (default
`surveillance/detector`) is joined with the payload's `camera` field,
giving `surveillance/detector/<camera>` per camera.

Auto-reconnect: paho's loop_forever retries on its own 1s -> 120s
backoff. While the broker is down, QoS0 publishes are queued locally
and flush on reconnect - the detector never blocks or drops frames.
And if the paho loop ever dies from a bug in our own callbacks
(a crash there would otherwise kill the transport permanently,
like the capture loop must never die): the thread recreates the
client and retries after 5s - the same retry shape as NatsPub.

Pure daemon - no stop()/join(): it dies at process exit, the kernel
closes the socket, and HiveMQ just sees a TCP close (clean session,
nothing retained).

The module uses the same `"detector"` logger (configured by main.py's
setup_logging at process start), so its lines land in the same journald
stream as the NATS lines.

NOTE: this file is `mqtt_pub.py` on purpose - a top-level module named
`mqtt.py` would shadow paho's `mqtt` package (same shadowing rule as
nats_pub.py).
"""

import json
import logging
import threading
import time

import paho.mqtt.client as paho
from paho.mqtt.enums import CallbackAPIVersion, MQTTErrorCode

logger = logging.getLogger("detector")


class MqttPub(threading.Thread):
    """Background MQTT publisher: auto-reconnect; mirrors NatsPub.

    Pure daemon - no stop()/join(): it dies at process exit, the kernel
    closes the socket, and HiveMQ just sees a TCP close.
    """

    def __init__(self, host, port, topic, user="", password="", client_id="detector"):
        super().__init__(daemon=True, name="mqtt")
        self.host, self.port, self.topic = host, port, topic
        self._user, self._pass, self._client_id = user, password, client_id
        self._c = self._make_client()
        self._pub_errors = 0

    def _make_client(self):
        """Fresh paho client with our callbacks. Note: paho's
        on_connect/on_disconnect callbacks (VERSION2 API) receive a
        ReasonCode enum, not an int - use rc.value, int(rc) raises."""
        c = paho.Client(CallbackAPIVersion.VERSION2, client_id=self._client_id)
        if self._user:
            c.username_pw_set(self._user, self._pass or None)
        c.on_connect = lambda cl, u, f, rc, props: logger.info(
            f"mqtt connected: {self.host}:{self.port} (topic {self.topic}, "
            f"rc={rc.value})"
        )
        c.on_disconnect = lambda cl, u, flags, rc, props: logger.info(
            f"mqtt disconnected (rc={rc.value}); paho auto-reconnect - "
            f"stills keep flowing"
        )
        return c

    def publish(self, payload):
        """Thread-safe: safe to call from the capture thread (or any thread).

        Queues QoS0 to paho's outbound queue; a broker outage is logged
        (first + every 50th), never raised - the capture loop must keep
        running no matter what the broker does.
        """
        cam = payload.get("camera", "")
        t = f"{self.topic}/{cam}" if cam else self.topic
        try:
            r = self._c.publish(t, json.dumps(payload, separators=(",", ":")), qos=0)
            rc = int(r.rc)
            if rc not in (
                int(MQTTErrorCode.MQTT_ERR_SUCCESS),
                int(MQTTErrorCode.MQTT_ERR_NO_CONN),  # queued while down - paho flushes on reconnect
            ):
                self._note(f"publish {t!r} rc={rc}")
        except Exception:
            self._note(f"publish {t!r} raised")

    def _note(self, what):
        self._pub_errors += 1
        if self._pub_errors == 1 or self._pub_errors % 50 == 0:
            logger.warning(f"mqtt publish error (#{self._pub_errors}): {what} - continuing")

    def run(self):
        # paho does the initial connect on the loop thread; while the
        # broker is down it retries on its own 1s -> 120s backoff. If
        # the loop itself dies (a bug in our callbacks), recreate the
        # client and retry - a transport must come back, like the
        # capture loop.
        while True:
            self._c = self._make_client()
            try:
                self._c.connect_async(self.host, self.port, keepalive=60)
                self._c.loop_forever(retry_first_connection=True)
            except Exception:
                logger.warning("mqtt loop ended; retry in 5s", exc_info=True)
                time.sleep(5)
