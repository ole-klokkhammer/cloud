#!/usr/bin/env python3
"""Matrix Backup Monitor Bot - monitors backup status and alerts on failures."""

import asyncio
import json
import os
import shlex
import time
from datetime import datetime
from pathlib import Path

from aiohttp import web
from nio import AsyncClient, RoomMessageText, LoginResponse

# Configuration
MATRIX_SERVER = os.getenv("MATRIX_SERVER", "https://matrix.home.lan")
MATRIX_USER = os.getenv("MATRIX_USER", "@backup-bot:home.lan")
MATRIX_PASSWORD = os.getenv("MATRIX_PASSWORD", "")
MATRIX_TOKEN = os.getenv("MATRIX_TOKEN", "")  # Use token OR password
MATRIX_ROOM = os.getenv("MATRIX_ROOM", "!backups:home.lan")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8090"))
STATE_FILE = os.getenv("STATE_FILE", "/data/backup_state.json")

# Optional ZFS monitoring
# Comma-separated dataset names to monitor, e.g. "tank/backups,tank/system"
ZFS_DATASETS = [d.strip() for d in os.getenv("ZFS_DATASETS", "").split(",") if d.strip()]
# Snapshot name filter (optional). Examples: "auto-", "backup-", "@zrepl_"
ZFS_SNAPSHOT_CONTAINS = os.getenv("ZFS_SNAPSHOT_CONTAINS", "")
# Max acceptable age since newest snapshot, per dataset (hours)
ZFS_MAX_AGE_HOURS = float(os.getenv("ZFS_MAX_AGE_HOURS", "24"))
# How often to check ZFS (seconds)
ZFS_CHECK_INTERVAL_SECONDS = int(os.getenv("ZFS_CHECK_INTERVAL_SECONDS", "3600"))

# Backup expectations (name -> max hours between backups)
BACKUP_SCHEDULE = {
    "core": 24,
    "media": 24,
    "config": 12,
    "database": 6,
}


class BackupState:
    """Track backup status."""

    def __init__(self, state_file: str):
        self.state_file = Path(state_file)
        self.backups: dict = {}
        self.load()

    def load(self):
        if self.state_file.exists():
            self.backups = json.loads(self.state_file.read_text())

    def save(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.backups, indent=2))

    def record(self, name: str, success: bool, message: str = ""):
        self.backups[name] = {
            "last_run": datetime.now().isoformat(),
            "success": success,
            "message": message,
        }
        self.save()

    def get_status(self) -> list[dict]:
        status = []
        now = datetime.now()
        for name, max_hours in BACKUP_SCHEDULE.items():
            info = self.backups.get(name, {})
            last_run = info.get("last_run")
            success = info.get("success", False)

            if last_run:
                last_dt = datetime.fromisoformat(last_run)
                age_hours = (now - last_dt).total_seconds() / 3600
                overdue = age_hours > max_hours
            else:
                age_hours = None
                overdue = True

            status.append({
                "name": name,
                "last_run": last_run,
                "age_hours": round(age_hours, 1) if age_hours else None,
                "success": success,
                "overdue": overdue,
                "message": info.get("message", ""),
            })
        return status


class BackupBot:
    """Matrix bot for backup monitoring."""

    def __init__(self):
        self.client = AsyncClient(MATRIX_SERVER, MATRIX_USER)
        self.state = BackupState(STATE_FILE)
        self.room_id = MATRIX_ROOM

    async def login(self):
        if MATRIX_TOKEN:
            self.client.access_token = MATRIX_TOKEN
            self.client.user_id = MATRIX_USER
        else:
            response = await self.client.login(MATRIX_PASSWORD)
            if not isinstance(response, LoginResponse):
                raise Exception(f"Login failed: {response}")
            print(f"Logged in as {self.client.user_id}")

    async def send(self, message: str):
        await self.client.room_send(
            self.room_id,
            "m.room.message",
            {"msgtype": "m.text", "body": message},
        )

    async def handle_message(self, room, event):
        if event.sender == self.client.user_id:
            return

        body = event.body.strip()
        if not body.startswith("!"):
            return

        cmd = body.split()[0].lower()
        args = body.split()[1:] if len(body.split()) > 1 else []

        if cmd == "!status":
            await self.cmd_status()
        elif cmd == "!help":
            await self.cmd_help()
        elif cmd == "!list":
            await self.cmd_list()
        elif cmd == "!check":
            await self.cmd_check()
        elif cmd in ("!zfs", "!zfsstatus"):
            await self.cmd_zfs_status()

    async def cmd_help(self):
        help_text = """📋 **Backup Bot Commands**
• `!status` - Show all backup status
• `!list` - List configured backups
• `!check` - Check for overdue backups
• `!zfs` - Show ZFS snapshot status (if enabled)
• `!help` - Show this help"""
        await self.send(help_text)

    async def cmd_status(self):
        status = self.state.get_status()
        lines = ["📊 **Backup Status**", ""]
        for s in status:
            icon = "✅" if s["success"] and not s["overdue"] else "❌" if not s["success"] else "⚠️"
            age = f"{s['age_hours']}h ago" if s["age_hours"] else "never"
            overdue = " (OVERDUE)" if s["overdue"] else ""
            lines.append(f"{icon} **{s['name']}**: {age}{overdue}")
        await self.send("\n".join(lines))

    async def cmd_list(self):
        lines = ["📋 **Configured Backups**", ""]
        for name, hours in BACKUP_SCHEDULE.items():
            lines.append(f"• {name}: every {hours}h")
        await self.send("\n".join(lines))

    async def cmd_check(self):
        status = self.state.get_status()
        overdue = [s for s in status if s["overdue"] or not s["success"]]
        if overdue:
            lines = ["🚨 **Attention Required**", ""]
            for s in overdue:
                reason = "OVERDUE" if s["overdue"] else "FAILED"
                lines.append(f"❌ {s['name']}: {reason}")
            await self.send("\n".join(lines))
        else:
            await self.send("✅ All backups healthy")

    async def cmd_zfs_status(self):
        if not ZFS_DATASETS:
            await self.send("ℹ️ ZFS monitoring is disabled (set `ZFS_DATASETS`).")
            return

        lines = ["🗄️ **ZFS Snapshot Status**", ""]
        try:
            status = await self._get_zfs_status()
        except Exception as exc:
            await self.send(f"❌ ZFS check failed: {exc}")
            return

        for item in status:
            icon = "✅" if item["ok"] else "❌"
            age = item["age_hours"]
            age_txt = f"{age:.1f}h" if age is not None else "never"
            extra = f" ({item['snapshot']})" if item.get("snapshot") else ""
            lines.append(f"{icon} **{item['dataset']}**: {age_txt}{extra}")

        await self.send("\n".join(lines))

    async def check_overdue_loop(self):
        """Periodically check for overdue backups (dead man's switch)."""
        # Initial check after 5 minutes
        await asyncio.sleep(300)
        await self._check_and_alert()

        # Then check every hour
        while True:
            await asyncio.sleep(3600)
            await self._check_and_alert()

    async def _check_and_alert(self):
        """Check for overdue or failed backups and alert."""
        status = self.state.get_status()
        problems = [s for s in status if s["overdue"] or not s["success"]]

        if problems:
            lines = ["🚨 **Backup Alert - Action Required**", ""]
            for s in problems:
                if s["age_hours"] is None:
                    reason = "⚠️ NEVER RUN"
                elif s["overdue"]:
                    expected = BACKUP_SCHEDULE.get(s["name"], 24)
                    reason = f"🕐 OVERDUE: last run {s['age_hours']}h ago (expected every {expected}h)"
                else:
                    reason = f"❌ FAILED: {s['message']}"
                lines.append(f"• **{s['name']}**: {reason}")

            lines.append("")
            lines.append("Run `!status` for full details")
            await self.send("\n".join(lines))

        # Also alert on ZFS snapshot problems if enabled
        if ZFS_DATASETS:
            try:
                zfs_status = await self._get_zfs_status()
            except Exception as exc:
                await self.send(f"❌ ZFS check failed: {exc}")
                return

            problems = [s for s in zfs_status if not s["ok"]]
            if problems:
                lines = ["🚨 **ZFS Snapshot Alert**", ""]
                for s in problems:
                    if s["age_hours"] is None:
                        reason = "⚠️ NO SNAPSHOT FOUND"
                    else:
                        reason = f"🕐 TOO OLD: {s['age_hours']:.1f}h (max {ZFS_MAX_AGE_HOURS}h)"
                    extra = f" ({s['snapshot']})" if s.get("snapshot") else ""
                    lines.append(f"• **{s['dataset']}**: {reason}{extra}")
                await self.send("\n".join(lines))

    async def check_zfs_loop(self):
        if not ZFS_DATASETS:
            return

        # Initial delay to avoid spamming on startup
        await asyncio.sleep(300)
        while True:
            await self._check_and_alert()
            await asyncio.sleep(ZFS_CHECK_INTERVAL_SECONDS)

    async def _get_zfs_status(self) -> list[dict]:
        """Return newest snapshot age per dataset.

        Requires `zfs` available where the bot runs and access to /dev/zfs.
        """

        # `zfs list -t snapshot -o name,creation -s creation -p -H`
        # Output example:
        # tank/ds@snap\t1700000000
        cmd = [
            "zfs",
            "list",
            "-t",
            "snapshot",
            "-o",
            "name,creation",
            "-s",
            "creation",
            "-p",
            "-H",
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(
                f"zfs command failed (exit {proc.returncode}): {stderr.decode(errors='replace').strip()}"
            )

        newest: dict[str, tuple[str, int]] = {}
        for raw_line in stdout.decode(errors="replace").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue

            snap_name = parts[0]
            if "@" not in snap_name:
                continue
            dataset = snap_name.split("@", 1)[0]
            if dataset not in ZFS_DATASETS:
                continue
            if ZFS_SNAPSHOT_CONTAINS and ZFS_SNAPSHOT_CONTAINS not in snap_name:
                continue

            try:
                created_epoch = int(parts[1])
            except ValueError:
                continue

            # Since list is sorted ascending, overwrite to keep newest
            newest[dataset] = (snap_name, created_epoch)

        now_epoch = int(time.time())
        status: list[dict] = []
        for dataset in ZFS_DATASETS:
            if dataset in newest:
                snap_name, created_epoch = newest[dataset]
                age_hours = (now_epoch - created_epoch) / 3600.0
                ok = age_hours <= ZFS_MAX_AGE_HOURS
                status.append(
                    {
                        "dataset": dataset,
                        "snapshot": snap_name,
                        "age_hours": age_hours,
                        "ok": ok,
                    }
                )
            else:
                status.append(
                    {
                        "dataset": dataset,
                        "snapshot": None,
                        "age_hours": None,
                        "ok": False,
                    }
                )

        return status

    async def run(self):
        await self.login()
        self.client.add_event_callback(self.handle_message, RoomMessageText)

        # Start background tasks
        asyncio.create_task(self.check_overdue_loop())
        asyncio.create_task(self.check_zfs_loop())
        asyncio.create_task(self.run_webhook())

        # Announce startup
        await self.send("🤖 Backup monitor bot started")

        # Sync forever
        await self.client.sync_forever(timeout=30000)

    async def run_webhook(self):
        """HTTP webhook to receive backup notifications."""

        async def handle_webhook(request):
            try:
                data = await request.json()
                name = data.get("name", "unknown")
                success = data.get("success", False)
                message = data.get("message", "")

                self.state.record(name, success, message)

                icon = "✅" if success else "❌"
                msg = f"{icon} **Backup: {name}**\n{message}" if message else f"{icon} Backup: {name}"
                await self.send(msg)

                return web.json_response({"status": "ok"})
            except Exception as e:
                return web.json_response({"error": str(e)}, status=400)

        app = web.Application()
        app.router.add_post("/webhook", handle_webhook)
        app.router.add_get("/health", lambda r: web.json_response({"status": "healthy"}))

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", WEBHOOK_PORT)
        await site.start()
        print(f"Webhook listening on port {WEBHOOK_PORT}")


async def main():
    bot = BackupBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
