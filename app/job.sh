#!/bin/bash

export GRAFANA_API_TOKEN_SOURCE="eyJrIjoiTWRod2FSaEYyOEkxWXFsYzRqMlBBVm5TZlFpSjg5WjciLCJuIjoiYXBpa2V5Y3VybCIsImlkIjoxfQ=="
export GRAFANA_API_TOKEN_DESTINATION="eyJrIjoiNnNDV3l6NUIxbXQ2ZUtEYWVrbUpESVJRa05zSHJSTlAiLCJuIjoiYXBpa2V5Y3VybCIsImlkIjoxfQ=="
export GRAFANA_DOMAIN_SOURCE="http://localhost:3000"
export GRAFANA_DOMAIN_DESTINATION="http://localhost:3001"

python3 dashboards_exporter.py
