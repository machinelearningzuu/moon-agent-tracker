import pytest
import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestNotificationService:
    """Tests for the Notification Service API."""

    def test_health_check(self, notification_service_url):
        """Test the health check endpoint."""
        response = requests.get(f"{notification_service_url}/notifications/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["database"] == "connected"

    # def test_get_all_notifications(self, notification_service_url):
    #     """Test retrieving all notifications."""
    #     response = requests.get(f"{notification_service_url}/notifications/")
    #     assert response.status_code == 200
    #     assert isinstance(response.json(), list)

    # def test_create_get_update_delete_notification(self, notification_service_url, test_notification):
    #     """Test the complete CRUD operations for a notification."""
    #     # Create notification
    #     response = requests.post(
    #         f"{notification_service_url}/notifications/",
    #         json=test_notification
    #     )
    #     assert response.status_code in [200, 201, 409], f"Failed to create notification: {response.text}"
        
    #     if response.status_code == 409:
    #         logger.info("Notification already exists, continuing with test...")
    #     else:
    #         logger.info(f"Created notification: {response.json()}")
    #         assert response.json()["notification_id"] == test_notification["notification_id"]

    #     # Get notification
    #     response = requests.get(f"{notification_service_url}/notifications/{test_notification['notification_id']}")
    #     assert response.status_code == 200
    #     assert response.json()["notification_id"] == test_notification["notification_id"]

    #     # Update notification
    #     updated_notification = test_notification.copy()
    #     updated_notification["status"] = "sent"
    #     response = requests.put(
    #         f"{notification_service_url}/notifications/{test_notification['notification_id']}",
    #         json=updated_notification
    #     )
    #     assert response.status_code == 200
    #     assert response.json()["status"] == "sent"

    #     # Delete notification
    #     response = requests.delete(f"{notification_service_url}/notifications/{test_notification['notification_id']}")
    #     assert response.status_code == 200
    #     assert "deleted successfully" in response.json()["message"].lower()

    #     # Verify deletion
    #     response = requests.get(f"{notification_service_url}/notifications/{test_notification['notification_id']}")
    #     assert response.status_code == 404

    # def test_get_notifications_by_recipient(self, notification_service_url, test_notification):
    #     """Test retrieving notifications by recipient ID."""
    #     # First create a notification
    #     response = requests.post(
    #         f"{notification_service_url}/notifications/",
    #         json=test_notification
    #     )
    #     initial_status = response.status_code
    #     if initial_status not in [200, 201, 409]:
    #         pytest.fail(f"Failed to create notification: {response.text}")

    #     # Get notifications by recipient
    #     response = requests.get(f"{notification_service_url}/notifications/recipient/{test_notification['recipient_id']}")
    #     assert response.status_code == 200
    #     assert isinstance(response.json(), list)
        
    #     # Clean up
    #     requests.delete(f"{notification_service_url}/notifications/{test_notification['notification_id']}")

    # def test_get_notifications_by_status(self, notification_service_url, test_notification):
    #     """Test retrieving notifications by status."""
    #     # First create a notification
    #     response = requests.post(
    #         f"{notification_service_url}/notifications/",
    #         json=test_notification
    #     )
    #     initial_status = response.status_code
    #     if initial_status not in [200, 201, 409]:
    #         pytest.fail(f"Failed to create notification: {response.text}")

    #     # Get notifications by status
    #     response = requests.get(f"{notification_service_url}/notifications/status/{test_notification['status']}")
    #     assert response.status_code == 200
    #     assert isinstance(response.json(), list)
        
    #     # Clean up
    #     requests.delete(f"{notification_service_url}/notifications/{test_notification['notification_id']}")

    # def test_get_notifications_by_type(self, notification_service_url, test_notification):
    #     """Test retrieving notifications by type."""
    #     # First create a notification
    #     response = requests.post(
    #         f"{notification_service_url}/notifications/",
    #         json=test_notification
    #     )
    #     initial_status = response.status_code
    #     if initial_status not in [200, 201, 409]:
    #         pytest.fail(f"Failed to create notification: {response.text}")

    #     # Get notifications by type
    #     response = requests.get(f"{notification_service_url}/notifications/type/{test_notification['type']}")
    #     assert response.status_code == 200
    #     assert isinstance(response.json(), list)
        
    #     # Clean up
    #     requests.delete(f"{notification_service_url}/notifications/{test_notification['notification_id']}")

    def test_get_nonexistent_notification(self, notification_service_url):
        """Test retrieving a non-existent notification."""
        response = requests.get(f"{notification_service_url}/notifications/nonexistent-notification")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_nonexistent_notification(self, notification_service_url, test_notification):
        """Test updating a non-existent notification."""
        updated_notification = test_notification.copy()
        updated_notification["status"] = "sent"
        response = requests.put(
            f"{notification_service_url}/notifications/nonexistent-notification",
            json=updated_notification
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_nonexistent_notification(self, notification_service_url):
        """Test deleting a non-existent notification."""
        response = requests.delete(f"{notification_service_url}/notifications/nonexistent-notification")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower() 