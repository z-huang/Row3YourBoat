from mitmproxy import http, ctx
import asyncio
import requests
import os
from urllib.parse import urlparse
from .auth import AuthManager
from .influxdb import InfluxDBManager

FRONTEND_HOST_ALIAS = os.getenv('FRONTEND_HOST_ALIAS')
FRONTEND_HOST = os.getenv('FRONTEND_HOST')
FRONTEND_PORT = int(os.getenv('FRONTEND_PORT'))


class SlackingPolicyEnforcer:
    def __init__(self, auth_manager: AuthManager, influx_manager: InfluxDBManager):
        self.auth_manager = auth_manager
        self.influx_manager = influx_manager

    def request(self, flow: http.HTTPFlow):
        username = self.auth_manager.get_username(flow)
        if not username:
            return

        if flow.request.pretty_host == FRONTEND_HOST_ALIAS:
            flow.request.host = FRONTEND_HOST
            flow.request.port = FRONTEND_PORT

        try:
            response = requests.post(
                "http://backend:8000/api/get_policy",
                json={
                    "username": username,
                    "url": flow.request.url
                }
            )
            response.raise_for_status()

            policy = response.json()
            if not policy['can_pass']:
                hostname = urlparse(flow.request.url).hostname
                asyncio.create_task(
                    self.influx_manager.log_slack(username, hostname))
                flow.response = http.Response.make(
                    302,
                    b"",
                    {
                        "Location": f"http://{FRONTEND_HOST_ALIAS}/slacking?token={policy['token']}"
                    }
                )
        except Exception as e:
            ctx.log.error(f"Error sending event to backend: {e}")
