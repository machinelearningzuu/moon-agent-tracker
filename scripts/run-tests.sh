#!/bin/bash

echo "Running basic health checks..."


curl -s http://localhost/agent-service/health || exit 1
curl -v http://localhost:8001/sales/health || exit 1
curl -v http://localhost:8002/notifications/health || exit 1

echo "All services passed health checks!"