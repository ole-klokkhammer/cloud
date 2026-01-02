# API
If multiple devices or services try to access the Bluetooth hardware through your API, you need to handle concurrency and hardware limitations.

Bluetooth hardware (the HCI controller) has specific behaviors when shared:

1. Scanning (Shared)
Multiple clients can request a scan at the same time. BlueZ (the Linux Bluetooth stack) is good at multiplexing this. If two people call GET /scan, the controller performs one scan and the API returns the results to both.

2. Connecting (Exclusive)
A BLE device can typically only have one active connection at a time. If Client A is connected to a heart rate monitor, Client B will receive a "Device Busy" or "Connection Failed" error if they try to connect to the same MAC address.

3. Hardware Commands (Sequential)
The Bluetooth controller can only process one low-level command at a time. If you send 100 requests simultaneously, the kernel queues them, which can lead to timeouts.

## setup