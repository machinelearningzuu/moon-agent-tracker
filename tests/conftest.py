import pytest
import os
import json
from typing import Dict

# Default local development URLs
DEFAULT_URLS = {
    "agent_service": "http://localhost:8000",
    "sales_service": "http://localhost:8001",
    "notification_service": "http://localhost:8002",
    "aggregator_service": "http://localhost:8003"
}

# EKS URLs (from the run-tests-eks.py file)
EKS_URLS = {
    "agent_service": "http://acdf5014b5fbe4efbbdc40ec5d4ec65e-1788477015.ap-southeast-1.elb.amazonaws.com:8000",
    "sales_service": "http://a472c4ad3313d4e7d8674b86e5626f30-906344873.ap-southeast-1.elb.amazonaws.com:8001",
    "notification_service": "http://af6c3b2808d3742b7887aea64a638dde-15200592.ap-southeast-1.elb.amazonaws.com:8002"
}

def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="local",
        help="Environment to run tests against: local or eks"
    )

@pytest.fixture(scope="session")
def base_urls(request) -> Dict[str, str]:
    """Returns the base URLs for the services based on the environment."""
    env = request.config.getoption("--env")
    if env == "eks":
        return EKS_URLS
    return DEFAULT_URLS

@pytest.fixture(scope="session")
def agent_service_url(base_urls) -> str:
    """Returns the base URL for the agent service."""
    return base_urls["agent_service"]

@pytest.fixture(scope="session")
def sales_service_url(base_urls) -> str:
    """Returns the base URL for the sales service."""
    return base_urls["sales_service"]

@pytest.fixture(scope="session")
def notification_service_url(base_urls) -> str:
    """Returns the base URL for the notification service."""
    return base_urls["notification_service"]

@pytest.fixture(scope="function")
def test_agent():
    """Returns a test agent for use in tests."""
    return {
        "agent_id": "test-agent-1",
        "name": "Test Agent",
        "email": "test@example.com",
        "phone": "123-456-7890",
        "branch_id": "test-branch-1",
        "team_id": "test-team-1",
        "products_allowed": "all",
        "status": "active"
    }

@pytest.fixture(scope="function")
def test_sale():
    """Returns a test sale for use in tests."""
    return {
        "sale_id": "test-sale-1",
        "agent_id": "test-agent-1",
        "customer_id": "test-customer-1",
        "product_id": "test-product-1",
        "sale_amount": 1000.0,
        "timestamp": "2023-10-10T10:00:00Z",
        "status": "completed",
        "branch_id": "test-branch-1",
        "team_id": "test-team-1"
    }

@pytest.fixture(scope="function")
def test_notification():
    """Returns a test notification for use in tests."""
    return {
        "notification_id": "test-notification-1",
        "recipient_id": "test-agent-1",
        "type": "sale_confirmation",
        "content": "Sale confirmed: test-sale-1",
        "status": "pending",
        "created_at": "2023-10-10T10:01:00Z"
    } 