import asyncio
import base64
from datetime import datetime
from typing import Optional
from mitmproxy import http, ctx, connection
import requests
import os
from urllib.parse import urlparse
from influxdb_client import Point
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

INFLUX_TOKEN = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")
INFLUX_ORG = os.getenv("DOCKER_INFLUXDB_INIT_ORG")
INFLUX_BUCKET = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET")

FRONTEND_HOST_ALIAS = os.getenv('FRONTEND_HOST_ALIAS')
FRONTEND_HOST = os.getenv('FRONTEND_HOST')
FRONTEND_PORT = os.getenv('FRONTEND_PORT')

REALM = os.getenv('PROXY_REALM')


class SlackingDetector:
    def __init__(self):
        self.connection_to_user = {}
        self.request_to_user = {}
        self.queue = asyncio.Queue()
        self.influx_client = None
        self.write_api = None
        asyncio.create_task(self.init_influxdb())

    async def init_influxdb(self):
        self.influx_client = InfluxDBClientAsync(
            url='http://influxdb:8086',
            token=INFLUX_TOKEN,
            org=INFLUX_ORG,
        )
        self.write_api = self.influx_client.write_api()

    def authenticate(self, flow: http.HTTPFlow) -> Optional[str]:
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
        ctx.log.info(f'[Request] {flow.client_conn.id}')

        # Frontend alias
        if flow.request.pretty_host == FRONTEND_HOST_ALIAS:
            flow.request.host = FRONTEND_HOST
            flow.request.port = FRONTEND_PORT

        if flow.client_conn.id in self.connection_to_user:
            username = self.connection_to_user[flow.client_conn.id]
        else:
            username = self.authenticate(flow)
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
            self.request_to_user[flow.client_conn.id] = username

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
                try:
                    hostname = urlparse(flow.request.url).hostname
                    asyncio.create_task(self.write_api.write(
                        bucket=INFLUX_BUCKET,
                        record=Point("slack")
                        .tag("username", username)
                        .field("hostname", hostname)
                        .time(datetime.now())
                    ))
                except Exception as e:
                    ctx.log.warn(f"Influx write error: {e}")
                flow.response = http.Response.make(
                    302, b"", {
                        'Location': f'http://{FRONTEND_HOST_ALIAS}/slacking?token={policy["token"]}'
                    }
                )
        except requests.exceptions.RequestException as e:
            ctx.log.error(f"Error sending event to backend: {e}")

        upload_size = len(flow.request.content or b'')
        if upload_size > 0:
            asyncio.create_task(self.write_api.write(
                bucket=INFLUX_BUCKET,
                record=Point("user_traffic")
                .tag("username", username)
                .field("upload_bytes", upload_size)
                .time(datetime.now())
            ))

    def responseheaders(self, flow: http.HTTPFlow):
        if flow.client_conn.id in self.connection_to_user:
            username = self.connection_to_user[flow.client_conn.id]
        elif flow.client_conn.id in self.request_to_user:
            username = self.request_to_user[flow.client_conn.id]
        else:
            ctx.log.error(
                f'[Response] {flow.client_conn.id} user not found!!!')
            return

        def callback(data: bytes):
            download_size = len(data)
            asyncio.create_task(self.write_api.write(
                bucket=INFLUX_BUCKET,
                record=Point("user_traffic")
                .tag("username", username)
                .field("download_bytes", download_size)
                .time(datetime.now())
            ))
            return data

        flow.response.stream = callback

    def response(self, flow: http.HTTPFlow):
        ctx.log.info(f'[Response] {flow.client_conn.id}')

        if flow.client_conn.id in self.request_to_user:
            del self.request_to_user[flow.client_conn.id]

    def http_connect(self, flow: http.HTTPFlow):
        ctx.log.info(f'[CONNECT] {flow.client_conn.id}')
        username = self.authenticate(flow)
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
            self.connection_to_user[flow.client_conn.id] = username

    def client_disconnected(self, client: connection.Client):
        ctx.log.info(f'[DISCONNECT] {client.id}')
        if client.id in self.connection_to_user:
            ctx.log.info(
                f'User {self.connection_to_user[client.id]} disconnected.')
            del self.connection_to_user[client.id]


addons = [
    SlackingDetector()
]
