#!/usr/bin/env python3
import os
import sys
import logging
import argparse
import subprocess
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Run API tests for microservices')
    parser.add_argument(
        '--env',
        choices=['local', 'eks'],
        default='local',
        help='Environment to run tests against (default: local)'
    )
    parser.add_argument(
        '--service',
        choices=['agent', 'sales', 'notification', 'integration', 'all'],
        default='all',
        help='Service to test (default: all)'
    )
    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate HTML report'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show verbose output'
    )
    return parser.parse_args()

def run_tests(args):
    """Run the tests based on the provided arguments."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Determine which tests to run
    if args.service == 'all':
        test_files = [
            'test_agent_service.py',
            'test_sales_service.py',
            'test_notification_service.py',
            'test_integration.py'
        ]
    else:
        service_map = {
            'agent': 'test_agent_service.py',
            'sales': 'test_sales_service.py',
            'notification': 'test_notification_service.py',
            'integration': 'test_integration.py'
        }
        test_files = [service_map[args.service]]
    
    # Build pytest command
    pytest_cmd = ['pytest']
    
    # Add environment
    pytest_cmd.extend(['--env', args.env])
    
    # Add HTML report if requested
    if args.html:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        report_dir = f"reports/{args.env}/{timestamp}"
        os.makedirs(f"reports/{args.env}", exist_ok=True)
        pytest_cmd.extend(['--html', f"{report_dir}/report.html", '--self-contained-html'])
    
    # Add verbose flag if requested
    if args.verbose:
        pytest_cmd.append('-v')
    
    # Add test files
    pytest_cmd.extend(test_files)
    
    # Run the tests
    logger.info(f"Running tests with command: {' '.join(pytest_cmd)}")
    try:
        subprocess.run(pytest_cmd, check=True)
        logger.info("Tests completed successfully")
        return 0
    except subprocess.CalledProcessError as e:
        logger.error(f"Tests failed with exit code {e.returncode}")
        return e.returncode

if __name__ == '__main__':
    args = parse_arguments()
    sys.exit(run_tests(args)) 