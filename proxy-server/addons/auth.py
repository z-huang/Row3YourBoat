import base64
from typing import Optional
import requests
from mitmproxy import ctx, http, connection
import os

REALM = os.getenv('PROXY_REALM')


class AuthManager:
    def __init__(self):
        self.connection_to_user = {}
        self.request_to_user = {}

    def make_407_response(self):
        return http.Response.make(
            407,
            b"Proxy Authentication Required",
            {
                "Proxy-Authenticate": f'Basic realm="{REALM}"',
                "Content-Length": "0"
            }
        )

    def authenticate(self, flow: http.HTTPFlow) -> Optional[str]:
        auth_header = flow.request.headers.get("Proxy-Authorization")
        if not auth_header:
            ctx.log.warn(f"Missing Proxy-Authorization header")
            flow.response = self.make_407_response()
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
                flow.response = self.make_407_response()
                return None
            else:
                return username

        except Exception as e:
            ctx.log.error(f"Auth error: {str(e)}")
            flow.response = self.make_407_response()
            return None

    def http_connect(self, flow: http.HTTPFlow):
        ctx.log.info(f'[CONNECT] {flow.client_conn.id}')

        username = self.authenticate(flow)
        if username is not None:
            self.connection_to_user[flow.client_conn.id] = username

    def client_disconnected(self, client: connection.Client):
        ctx.log.info(f'[DISCONNECT] {client.id}')

        if client.id in self.connection_to_user:
            del self.connection_to_user[client.id]

    def request(self, flow: http.HTTPFlow):
        ctx.log.info(f'[Request] {flow.client_conn.id}')

        if flow.client_conn.id not in self.connection_to_user:
            username = self.authenticate(flow)
            if username is not None:
                self.request_to_user[flow.client_conn.id] = username

    def response(self, flow: http.HTTPFlow):
        ctx.log.info(f'[Response] {flow.client_conn.id}')

        if flow.client_conn.id in self.request_to_user:
            del self.request_to_user[flow.client_conn.id]

    def get_username(self, flow: http.HTTPFlow) -> Optional[str]:
        if flow.client_conn.id in self.connection_to_user:
            return self.connection_to_user[flow.client_conn.id]
        if flow.client_conn.id in self.request_to_user:
            return self.request_to_user[flow.client_conn.id]
        return None
