FROM grafana/grafana-oss:latest

# Copy provisioning configs
COPY provisioning/dashboards.yaml /etc/grafana/provisioning/dashboards/dashboards.yaml
COPY provisioning/datasources.yaml /etc/grafana/provisioning/datasources/datasources.yaml

# Copy dashboard JSONs
COPY dashboards /etc/grafana/provisioning/dashboards/