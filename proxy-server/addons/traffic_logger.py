from mitmproxy import http
import asyncio
from .auth import AuthManager
from .influxdb import InfluxDBManager


class TrafficLogger:
    def __init__(self, auth_manager: AuthManager, influx_manager: InfluxDBManager):
        self.auth_manager = auth_manager
        self.influx_manager = influx_manager

    def request(self, flow: http.HTTPFlow):
        username = self.auth_manager.get_username(flow)
        if not username:
            return

        upload_size = len(flow.request.content or b'')
        if upload_size > 0:
            asyncio.create_task(self.influx_manager.log_traffic(
                username,
                upload=upload_size
            ))

    def responseheaders(self, flow: http.HTTPFlow):
        username = self.auth_manager.get_username(flow)
        if not username:
            return

        def callback(data: bytes):
            download_size = len(data)
            asyncio.create_task(self.influx_manager.log_traffic(
                username,
                download=download_size
            ))
            return data

        flow.response.stream = callback
