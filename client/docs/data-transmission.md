# Data transmission contract

## Sensor data (TCP)

- Destination: `SERVER_ADDR` and `SERVER_PORT`, overridable with `--server-addr` and `--server-port`.
- Transport: TCP JSON Lines. Each UTF-8 JSON payload ends with one newline; server replies with one newline-terminated JSON acknowledgement after CSV storage succeeds.
- Payload shape:

```json
{
  "client_id": "string",
  "region": "string",
  "datetime": "YYYY-MM-DD weekday HH:MM:SS",
  "session_id": "UUID",
  "sequence": 1,
  "sensor_data": {
    "temperature": 0.0,
    "humidity": 0.0,
    "pressure": 0.0,
    "co2": 0
  }
}
```

- A payload is sent only when all three sensor reads succeed. A read failure is reported by the healthcheck instead.
- `session_id` identifies one client process. `sequence` starts at 1 and increments for each send attempt in that process.
- Sender success means a matching `ok: true` server acknowledgement was received after CSV storage. The acknowledgement returns the server's cumulative `received_count` for that client.
- Server deduplicates the same `client_id`, `session_id`, and `sequence` tuple.

## Health and notifications

- Healthcheck: HTTP `POST` JSON to `WEB_HEALTH_URL`; it reports sensor, runtime, and TCP-send state, including cumulative `server_send.success_count`.
- Healthcheck: `health_report` tracks its own success/failure state; the result of one report is included in the next report.
- Discord notifications: sensor reads, health reports, and TCP server sends notify once when their consecutive failure count reaches the configured threshold, then notify once on recovery.
- Lifecycle: client start and normal stop notify Discord. Forced termination and power loss cannot send a stop notification.
- Settings: `SENSOR_FAILURE_NOTIFY_THRESHOLD`, `HEALTH_REPORT_FAILURE_NOTIFY_THRESHOLD`, and `SERVER_SEND_FAILURE_NOTIFY_THRESHOLD` default to 3.
- `--no-notify` disables Discord notifications for automated integration runs.
- Discord webhook requests include `User-Agent: smart-environment-monitor/1.0`.

## Change procedure

When the sensor TCP payload, transport, destination selection, send condition, or failure semantics changes:

1. Update this document, including a dated entry below and compatibility impact.
2. Update the matching TCP/health contract test in `client/tests`.
3. If the change requires server behavior, ship the client and server change together; do not silently change the wire format.

## Change log

- 2026-06-22: Documented existing TCP JSON contract and its lack of framing/acknowledgement. No wire-format change.
- 2026-06-22: Moved DHT22 device driver under `adapters/sensors/lib/`. No wire-format change.
- 2026-06-22: Added a fixed Discord webhook `User-Agent` to avoid Cloudflare error 1010. No TCP wire-format change.
- 2026-06-22: Added `server_send.success_count` to the healthcheck payload. No TCP wire-format change.
- 2026-06-22: Changed TCP sensor protocol to JSON Lines with storage ACK; added `session_id` and `sequence`. Client success now means acknowledged server storage.
- 2026-06-22: Added threshold and recovery Discord notifications for sensors, health reports, TCP sends, and client lifecycle events.
