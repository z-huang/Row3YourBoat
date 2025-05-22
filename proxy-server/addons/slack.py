from mitmproxy import http
import asyncio
import os
from .auth import AuthManager
from influxdb import InfluxDB
from db import Database

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

    async def request(self, flow: http.HTTPFlow):
        username = self.auth_manager.get_username(flow)
        if not username:
            return

        hostname = flow.request.pretty_host
        can_pass = self.db.check_host(hostname)
        if not can_pass:
            asyncio.create_task(self.influxdb.log_slack(username, hostname))
            token = self.db.record_slack(username, flow.request.url)
            flow.response = http.Response.make(
                302,
                b"",
                {
                    "Location": f"http://{DOMAIN}/slacking?token={token}"
                }
            )
