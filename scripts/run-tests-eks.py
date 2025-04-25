import requests, sys, os
import subprocess
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

def run_health_checks():
    print("🚦 Running integration health checks on EKS...")

    check_health("Agent Service", "http://acdf5014b5fbe4efbbdc40ec5d4ec65e-1788477015.ap-southeast-1.elb.amazonaws.com:8000/agents/health")
    check_health("Sales Service", "http://a472c4ad3313d4e7d8674b86e5626f30-906344873.ap-southeast-1.elb.amazonaws.com:8001/sales/health")
    check_health("Notification Service", "http://af6c3b2808d3742b7887aea64a638dde-15200592.ap-southeast-1.elb.amazonaws.com:8002/notifications/health")

    print("\n🎉 All services passed health checks on EKS!")

def run_api_tests():
    """Run the comprehensive API tests suite."""
    print("\n🧪 Running comprehensive API tests on EKS...")
    
    # Determine the path to the tests directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    tests_dir = os.path.join(project_root, "tests")
    
    # Run the tests with HTML report
    try:
        cmd = [
            sys.executable, 
            os.path.join(tests_dir, "run_tests.py"), 
            "--env", "eks", 
            "--html"
        ]
        subprocess.run(cmd, check=True)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        print(f"\n🎉 All API tests completed successfully!")
        print(f"📊 Test report is available in tests/reports/eks/ directory")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ API tests failed with exit code {e.returncode}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    # First run the basic health checks
    run_health_checks()
    
    # Then run the comprehensive API tests
    run_api_tests()

# """
# cd "C:\Users\zuuap\Dropbox\MSC BIG DATA ANALYTICS\CMM707 - Cloud Computing\Coursework"
# .venv\Scripts\activate.bat
# python scripts/run-tests-eks.py
# """