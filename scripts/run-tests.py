import requests
import sys

def check_health(name, url):
    print(f"🔍 Checking {name} at {url} ...")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name} is healthy: {response.json()}")
        else:
            print(f"❌ {name} returned status {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ {name} health check failed: {e}")
        sys.exit(1)

print("🚦 Running integration health checks...\n")

check_health("Agent Service", "http://127.0.0.1:8000/agents/health")
check_health("Sales Service", "http://127.0.0.1:8001/sales/health")
check_health("Notification Service", "http://127.0.0.1:8002/notifications/health")

print("\n🎉 All services passed health checks!")