import pytest
import requests
import json
import logging
import uuid
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestIntegration:
    """Tests for the integration between microservices."""

    def test_health_checks(self, agent_service_url, sales_service_url, notification_service_url):
        """Test that all services are healthy."""
        # Check agent service
        response = requests.get(f"{agent_service_url}/agents/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

        # Check sales service
        response = requests.get(f"{sales_service_url}/sales/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

        # Check notification service
        response = requests.get(f"{notification_service_url}/notifications/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    # def test_create_agent_sale_notification_flow(self, agent_service_url, sales_service_url, notification_service_url):
    #     """Test the complete flow from creating an agent to a sale to a notification."""
    #     # Generate unique IDs for this test
    #     test_id = str(uuid.uuid4())[:8]
    #     agent_id = f"test-agent-{test_id}"
    #     sale_id = f"test-sale-{test_id}"
    #     notification_id = f"test-notification-{test_id}"
        
    #     try:
    #         # 1. Create an agent
    #         agent_data = {
    #             "agent_id": agent_id,
    #             "name": f"Test Agent {test_id}",
    #             "email": f"test{test_id}@example.com",
    #             "phone": "123-456-7890",
    #             "branch_id": "test-branch-1",
    #             "team_id": "test-team-1",
    #             "products_allowed": "all",
    #             "status": "active"
    #         }
            
    #         response = requests.post(
    #             f"{agent_service_url}/agents/",
    #             json=agent_data
    #         )
    #         assert response.status_code in [200, 201, 409], f"Failed to create agent: {response.text}"
    #         logger.info(f"Created agent: {agent_id}")
            
    #         # 2. Create a sale for this agent
    #         sale_data = {
    #             "sale_id": sale_id,
    #             "agent_id": agent_id,
    #             "customer_id": "test-customer-1",
    #             "product_id": "test-product-1",
    #             "sale_amount": 1500.0,
    #             "timestamp": datetime.now().isoformat(),
    #             "status": "completed",
    #             "branch_id": "test-branch-1",
    #             "team_id": "test-team-1"
    #         }
            
    #         response = requests.post(
    #             f"{sales_service_url}/sales/",
    #             json=sale_data
    #         )
    #         assert response.status_code in [200, 201, 409], f"Failed to create sale: {response.text}"
    #         logger.info(f"Created sale: {sale_id}")
            
    #         # 3. Create a notification for this sale and agent
    #         notification_data = {
    #             "notification_id": notification_id,
    #             "recipient_id": agent_id,
    #             "type": "sale_confirmation",
    #             "content": f"Sale confirmed: {sale_id}",
    #             "status": "pending",
    #             "created_at": datetime.now().isoformat()
    #         }
            
    #         response = requests.post(
    #             f"{notification_service_url}/notifications/",
    #             json=notification_data
    #         )
    #         assert response.status_code in [200, 201, 409], f"Failed to create notification: {response.text}"
    #         logger.info(f"Created notification: {notification_id}")
            
    #         # 4. Check if the agent exists
    #         response = requests.get(f"{agent_service_url}/agents/{agent_id}")
    #         assert response.status_code == 200
    #         assert response.json()["agent_id"] == agent_id
            
    #         # 5. Check if the sale exists and is associated with the agent
    #         response = requests.get(f"{sales_service_url}/sales/{sale_id}")
    #         assert response.status_code == 200
    #         assert response.json()["sale_id"] == sale_id
    #         assert response.json()["agent_id"] == agent_id
            
    #         # 6. Check if the notification exists and is associated with the agent
    #         response = requests.get(f"{notification_service_url}/notifications/{notification_id}")
    #         assert response.status_code == 200
    #         assert response.json()["notification_id"] == notification_id
    #         assert response.json()["recipient_id"] == agent_id
            
    #         # 7. Verify sales can be queried by agent
    #         response = requests.get(f"{sales_service_url}/sales/agent/{agent_id}")
    #         assert response.status_code == 200
    #         sales = response.json()
    #         assert isinstance(sales, list)
    #         assert any(sale["sale_id"] == sale_id for sale in sales)
            
    #         # 8. Verify notifications can be queried by recipient
    #         response = requests.get(f"{notification_service_url}/notifications/recipient/{agent_id}")
    #         assert response.status_code == 200
    #         notifications = response.json()
    #         assert isinstance(notifications, list)
    #         assert any(notification["notification_id"] == notification_id for notification in notifications)
            
    #         # 9. Update the notification status to "sent"
    #         notification_data["status"] = "sent"
    #         response = requests.put(
    #             f"{notification_service_url}/notifications/{notification_id}",
    #             json=notification_data
    #         )
    #         assert response.status_code == 200
    #         assert response.json()["status"] == "sent"
            
    #         logger.info("Integration test flow completed successfully")
            
    #     finally:
    #         # Clean up: Delete all created resources in reverse order
    #         logger.info("Cleaning up test resources...")
            
    #         # Delete notification
    #         requests.delete(f"{notification_service_url}/notifications/{notification_id}")
            
    #         # Delete sale
    #         requests.delete(f"{sales_service_url}/sales/{sale_id}")
            
    #         # Delete agent
    #         requests.delete(f"{agent_service_url}/agents/{agent_id}")

    def test_nonexistent_agent_references(self, sales_service_url, notification_service_url):
        """Test that services correctly handle references to non-existent agents."""
        # Try to get sales for a non-existent agent
        response = requests.get(f"{sales_service_url}/sales/agent/nonexistent-agent")
        assert response.status_code in [200, 404]  # Some may return empty array, others 404
        
        if response.status_code == 200:
            assert len(response.json()) == 0  # Should return empty array
        
        # Try to get notifications for a non-existent agent
        response = requests.get(f"{notification_service_url}/notifications/recipient/nonexistent-agent")
        assert response.status_code in [200, 404]  # Some may return empty array, others 404
        
        if response.status_code == 200:
            assert len(response.json()) == 0  # Should return empty array 