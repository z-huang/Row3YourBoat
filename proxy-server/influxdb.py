from influxdb_client import InfluxDBClient, Point
import os
from datetime import datetime


class InfluxDB:
    def __init__(self):
        self.token = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")
        self.org = os.getenv("DOCKER_INFLUXDB_INIT_ORG")
        self.bucket = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET")

        self.client = InfluxDBClient(
            url='http://influxdb:8086',
            token=self.token,
            org=self.org,
        )
        self.write_api = self.client.write_api()

    def log_traffic(self, username, upload=0, download=0):
        point = Point("user_traffic").tag(
            "username", username).time(datetime.now())
        if upload:
            point.field("upload_bytes", upload)
        if download:
            point.field("download_bytes", download)
        self.write_api.write(bucket=self.bucket, record=point)

    def log_slack(self, username, hostname):
        point = Point("slack").tag("username", username).field(
            "hostname", hostname).time(datetime.now())
        self.write_api.write(bucket=self.bucket, record=point)
