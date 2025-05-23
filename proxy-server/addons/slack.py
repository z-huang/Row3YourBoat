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

    def request(self, flow: http.HTTPFlow):
        username = self.auth_manager.get_username(flow)
        if not username:
            return

        hostname = flow.request.pretty_host
        can_pass = self.db.check_host(hostname)

        if can_pass:
            return

        self.influxdb.log_slack(username, hostname)
        token = self.db.record_slack(username, flow.request.url)

        mode = self.db.get_global_mode()

        if mode is AccessMode.A or mode is AccessMode.C:
            flow.response = http.Response.make(
                302, b"",
                {
                    "Location": f"http://{DOMAIN}/slacking?token={token}"
                }
            )

        if mode is AccessMode.B or mode is AccessMode.C:
            notify_all_users_of_slack(username, flow.request.url, self.db)
