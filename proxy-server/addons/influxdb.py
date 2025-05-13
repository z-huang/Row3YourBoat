from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client import Point
import os
from datetime import datetime

class InfluxDBManager:
    def __init__(self):
        self.client = None
        self.write_api = None
        self.token = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")
        self.org = os.getenv("DOCKER_INFLUXDB_INIT_ORG")
        self.bucket = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET")

    async def init(self):
        self.client = InfluxDBClientAsync(
            url='http://influxdb:8086',
            token=self.token,
            org=self.org,
        )
        self.write_api = self.client.write_api()

    async def log_traffic(self, username, upload=0, download=0):
        point = Point("user_traffic").tag("username", username).time(datetime.now())
        if upload:
            point.field("upload_bytes", upload)
        if download:
            point.field("download_bytes", download)
        await self.write_api.write(bucket=self.bucket, record=point)

    async def log_slack(self, username, hostname):
        point = Point("slack").tag("username", username).field("hostname", hostname).time(datetime.now())
        await self.write_api.write(bucket=self.bucket, record=point)
