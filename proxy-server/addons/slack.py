from mitmproxy import http, ctx
import os
from .auth import AuthManager
from influxdb import InfluxDB
from db import Database, AccessMode
from alert import notify_all_users_of_slack

DOMAIN = os.getenv('DOMAIN')


class SlackingPolicyEnforcer:
    def __init__(
        self,
        auth_manager: AuthManager,
        db: Database,
        influxdb: InfluxDB
    ):
        self.auth_manager = auth_manager
        self.db = db
        self.influxdb = influxdb

    def _broadcast(self, username: str, url: str):
        host = http.url.parse(url).host
        token = self.db.record_slack(username, url)
        asyncio.create_task(self.influxdb.log_slack(username, host))
        # mail
        try:
            notify_all_users_of_slack(username, url, self.db)
        except Exception as e:
            ctx.log.warn(f"notify_all_users_of_slack failed: {e}")
        return token

    def _block(self, flow: http.HTTPFlow, token: str | None = None, reason="blocked"):
        flow.response = http.Response.make(
            302, b"", f"http://{DOMAIN}/slacking?token={token}"
        )

    def request(self, flow: http.HTTPFlow):
        username = self.auth_manager.get_username(flow)
        if not username:
            return

        hostname = flow.request.pretty_host
        can_pass = self.db.check_host(hostname)

        if can_pass:
            ctx.log.debug(f"Pass: {host}")
            return 

        mode = self.db.get_global_mode()

        if mode is AccessMode.A: 
            ctx.log.info(f"[Mode A] Block {username} -> {host}")
            self._block(flow, None, "modeA")

        elif mode is AccessMode.B:
            ctx.log.info(f"[Mode B] Mirror {username} -> {host}")
            self._broadcast(username, flow.request.url)

        elif mode is AccessMode.C:
            ctx.log.info(f"[Mode C] Block + Mirror {username} -> {host}")
            token = self._broadcast(username, flow.request.url)
            self._block(flow, token, "modeC")
        else:
            ctx.log.warn(f"Unknown mode {mode}, Error!")