from mitmproxy import http, ctx
import os
DOMAIN = os.getenv('DOMAIN')


class RedirectManager:
    def redirect(self, flow: http.HTTPFlow):
        hostname = flow.request.pretty_host
        if hostname == DOMAIN:
            flow.request.host = 'frontend'
            flow.request.port = 80
            flow.request.scheme = "http"
        elif hostname == f'backend.{DOMAIN}':
            flow.request.host = 'backend'
            flow.request.port = 8000
            flow.request.scheme = "http"
        elif hostname == f'grafana.{DOMAIN}':
            flow.request.host = 'grafana'
            flow.request.port = 3000
            flow.request.scheme = "http"
        elif hostname == f'influxdb.{DOMAIN}':
            flow.request.host = 'influxdb'
            flow.request.port = 8086
            flow.request.scheme = "http"

    async def request(self, flow: http.HTTPFlow):
        self.redirect(flow)

    async def http_connect(self, flow: http.HTTPFlow):
        self.redirect(flow)
