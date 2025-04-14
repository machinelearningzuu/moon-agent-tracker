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

print("🚦 Running integration health checks on EKS...")

check_health("Agent Service", "http://acdf5014b5fbe4efbbdc40ec5d4ec65e-1788477015.ap-southeast-1.elb.amazonaws.com:8000/agents/health")
check_health("Sales Service", "http://a472c4ad3313d4e7d8674b86e5626f30-906344873.ap-southeast-1.elb.amazonaws.com:8001/sales/health")
check_health("Notification Service", "http://af6c3b2808d3742b7887aea64a638dde-15200592.ap-southeast-1.elb.amazonaws.com:8002/notifications/health")

print("\n🎉 All services passed health checks on EKS!")

# """
# cd "C:\Users\zuuap\Dropbox\MSC BIG DATA ANALYTICS\CMM707 - Cloud Computing\Coursework"
# .venv\Scripts\activate.bat
# python scripts/run-tests-eks.py
# """