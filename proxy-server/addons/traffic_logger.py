from mitmproxy import http
from .auth import AuthManager
from influxdb import InfluxDB


class TrafficLogger:
    def __init__(self, auth_manager: AuthManager, influxdb: InfluxDB):
        self.auth_manager = auth_manager
        self.influxdb = influxdb

    def request(self, flow: http.HTTPFlow):
        username = self.auth_manager.get_username(flow)
        if not username:
            return

        upload_size = len(flow.request.content or b'')
        if upload_size > 0:
            self.influxdb.log_traffic(
                username,
                upload=upload_size
            )

    def responseheaders(self, flow: http.HTTPFlow):
        username = self.auth_manager.get_username(flow)
        if not username:
            return

        def callback(data: bytes):
            download_size = len(data)
            self.influxdb.log_traffic(
                username,
                download=download_size
            )
            return data

        flow.response.stream = callback
