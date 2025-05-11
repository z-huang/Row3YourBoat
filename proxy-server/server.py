import base64
from typing import Optional, Tuple
from mitmproxy import http, ctx, connection
import requests
import os

FRONTEND_URL = os.getenv('FRONTEND_URL')
REALM = os.getenv('PROXY_REALM')


class SlackingDetector:
    def __init__(self):
        self.conn_to_user = {}

    def _authenticate(self, flow: http.HTTPFlow) -> Optional[str]:
        auth_header = flow.request.headers.get("Proxy-Authorization")
        if not auth_header:
            ctx.log.warn(f"Missing Proxy-Authorization header")
            return None

        try:
            method, encoded = auth_header.split(" ", 1)
            if method.lower() != "basic":
                raise ValueError("Only Basic authentication is supported.")

            decoded = base64.b64decode(encoded.strip()).decode()
            username, password = decoded.split(":", 1)

            response = requests.post(
                'http://backend:8000/api/auth',
                json={
                    "username": username,
                    "password": password
                }
            )
            response.raise_for_status()
            authenticated = response.json().get("is_authenticated", False)
            if not authenticated:
                ctx.log.warn(f"Authentication failed for {username}")
                return None
            else:
                return username
        except Exception as e:
            ctx.log.error(f"Auth error: {str(e)}")
            return None

    def request(self, flow: http.HTTPFlow):
        ctx.log.info(
            f'[REQUEST] {flow.request.headers.get('Proxy-Authorization')}')
        username = (self.conn_to_user.get(flow.client_conn.id) or
                    self._authenticate(flow))
        if username is None:
            flow.response = http.Response.make(
                407,
                b"Proxy Authentication Required",
                {
                    "Proxy-Authenticate": f'Basic realm="{REALM}"',
                    "Content-Length": "0"
                }
            )
            return

        ctx.log.info(f'User {username} sent a request')

        try:
            response = requests.post(
                'http://backend:8000/api/get_policy',
                json={
                    'username': username,
                    'url': flow.request.url,
                }
            )
            response.raise_for_status()
            policy = response.json()
            if not policy['can_pass']:
                flow.response = http.Response.make(
                    302, b"", {
                        'Location': f'{FRONTEND_URL}/slacking?token={policy["token"]}'
                    }
                )
        except requests.exceptions.RequestException as e:
            ctx.log.error(f"Error sending event to backend: {e}")

    def http_connect(self, flow: http.HTTPFlow):
        ctx.log.info(
            f'[CONNECT] {flow.request.headers.get('Proxy-Authorization')}')
        username = self._authenticate(flow)
        if username is None:
            ctx.log.info(f'Ask for authentication')
            flow.response = http.Response.make(
                407,
                b"Proxy Authentication Required",
                {
                    "Proxy-Authenticate": f'Basic realm="{REALM}"',
                    "Content-Length": "0"
                }
            )
        else:
            ctx.log.info(f'User {username} connected.')
            self.conn_to_user[flow.client_conn.id] = username

    def client_disconnected(self, client: connection.Client):
        if client.id in self.conn_to_user:
            ctx.log.info(f'User {self.conn_to_user[client.id]} disconnected.')
            del self.conn_to_user[client.id]


addons = [
    SlackingDetector()
]
