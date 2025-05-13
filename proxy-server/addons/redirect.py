from mitmproxy import http, ctx
import os
DOMAIN = os.getenv('DOMAIN')


class RedirectManager:
    def request(self, flow: http.HTTPFlow):
        hostname = flow.request.pretty_host
        if hostname == DOMAIN:
            flow.request.host = 'frontend'
            flow.request.port = 80
        elif hostname == f'backend.{DOMAIN}':
            flow.request.host = 'backend'
            flow.request.port = 8000
        elif hostname == f'grafana.{DOMAIN}':
            flow.request.host = 'grafana'
            flow.request.port = 3000
        elif hostname == f'influxdb.{DOMAIN}':
            flow.request.host = 'influxdb'
            flow.request.port = 8086
