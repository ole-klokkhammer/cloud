# Matrix Backup Monitor Bot

A Matrix bot that monitors backup jobs and alerts on failures or overdue backups.

## Features

- **Commands**: `!status`, `!list`, `!check`, `!help`
- **Webhook**: Receive backup notifications via HTTP POST
- **Auto-alerts**: Hourly check for overdue backups
- **State tracking**: Persists backup history

## Setup

### 1. Create Matrix bot account

```bash
# Register bot user (or use Element)
curl -X POST "https://matrix.home.lan/_matrix/client/r0/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"backup-bot","password":"secure-password","auth":{"type":"m.login.dummy"}}'
```

### 2. Get access token

```bash
curl -X POST "https://matrix.home.lan/_matrix/client/r0/login" \
  -H "Content-Type: application/json" \
  -d '{"type":"m.login.password","user":"backup-bot","password":"secure-password"}' | jq .access_token
```

### 3. Invite bot to room

In Element or via API, invite `@backup-bot:home.lan` to your backups room.

### 4. Run the bot

```bash
# Local
export MATRIX_SERVER="https://matrix.home.lan"
export MATRIX_TOKEN="syt_your_token"
export MATRIX_ROOM="!roomid:home.lan"
python bot.py

# Docker
docker build -t matrix-backup-bot .
docker run -d \
  -e MATRIX_SERVER="https://matrix.home.lan" \
  -e MATRIX_TOKEN="syt_your_token" \
  -e MATRIX_ROOM="!roomid:home.lan" \
  -v /data/backup-bot:/data \
  -p 8090:8090 \
  matrix-backup-bot
```

## Webhook Usage

Send backup results to the bot:

```bash
# Success
curl -X POST http://backup-bot:8090/webhook \
  -H "Content-Type: application/json" \
  -d '{"name":"core","success":true,"message":"Backed up 50GB in 5m"}'

# Failure
curl -X POST http://backup-bot:8090/webhook \
  -H "Content-Type: application/json" \
  -d '{"name":"database","success":false,"message":"Connection refused"}'
```

## Integration with Backup Scripts

```bash
#!/bin/bash
# backup.sh

WEBHOOK="http://backup-bot.home.lan:8090/webhook"
NAME="core"

restic backup /data --repo s3:... 2>&1
STATUS=$?

if [ $STATUS -eq 0 ]; then
  curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" \
    -d "{\"name\":\"$NAME\",\"success\":true,\"message\":\"Completed at $(date)\"}"
else
  curl -sS -X POST "$WEBHOOK" -H "Content-Type: application/json" \
    -d "{\"name\":\"$NAME\",\"success\":false,\"message\":\"Exit code: $STATUS\"}"
fi
```

## Commands

| Command | Description |
|---------|-------------|
| `!status` | Show all backup status with age |
| `!list` | List configured backup schedules |
| `!check` | Alert on any overdue/failed backups |
| `!help` | Show available commands |

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MATRIX_SERVER` | `https://matrix.home.lan` | Matrix homeserver URL |
| `MATRIX_USER` | `@backup-bot:home.lan` | Bot user ID |
| `MATRIX_TOKEN` | - | Access token (or use PASSWORD) |
| `MATRIX_PASSWORD` | - | Password (if not using token) |
| `MATRIX_ROOM` | `!backups:home.lan` | Room to monitor |
| `WEBHOOK_PORT` | `8090` | HTTP webhook port |
| `STATE_FILE` | `/data/backup_state.json` | State persistence |

Edit `BACKUP_SCHEDULE` in `bot.py` to configure expected backup frequency.
