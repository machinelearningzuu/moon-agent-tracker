import pytest
import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestSalesService:
    """Tests for the Sales Service API."""

    def test_health_check(self, sales_service_url):
        """Test the health check endpoint."""
        response = requests.get(f"{sales_service_url}/sales/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["database"] == "connected"

    # def test_get_all_sales(self, sales_service_url):
    #     """Test retrieving all sales."""
    #     response = requests.get(f"{sales_service_url}/sales/")
    #     assert response.status_code == 200
    #     assert isinstance(response.json(), list)

    def test_create_get_update_delete_sale(self, sales_service_url, test_sale):
        """Test the complete CRUD operations for a sale."""
        # Create sale
        response = requests.post(
            f"{sales_service_url}/sales/",
            json=test_sale
        )
        assert response.status_code in [200, 201, 409], f"Failed to create sale: {response.text}"
        
        if response.status_code == 409:
            logger.info("Sale already exists, continuing with test...")
        else:
            logger.info(f"Created sale: {response.json()}")
            assert response.json()["sale_id"] == test_sale["sale_id"]

        # Get sale
        response = requests.get(f"{sales_service_url}/sales/{test_sale['sale_id']}")
        assert response.status_code == 200
        assert response.json()["sale_id"] == test_sale["sale_id"]

        # Update sale
        updated_sale = test_sale.copy()
        updated_sale["sale_amount"] = 2000.0
        response = requests.put(
            f"{sales_service_url}/sales/{test_sale['sale_id']}",
            json=updated_sale
        )
        assert response.status_code == 200
        assert response.json()["sale_amount"] == 2000.0

        # Delete sale
        response = requests.delete(f"{sales_service_url}/sales/{test_sale['sale_id']}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()

        # Verify deletion
        response = requests.get(f"{sales_service_url}/sales/{test_sale['sale_id']}")
        assert response.status_code == 404

    # def test_get_sales_by_agent(self, sales_service_url, test_sale):
    #     """Test retrieving sales by agent ID."""
    #     # First create a sale
    #     response = requests.post(
    #         f"{sales_service_url}/sales/",
    #         json=test_sale
    #     )
    #     initial_status = response.status_code
    #     if initial_status not in [200, 201, 409]:
    #         pytest.fail(f"Failed to create sale: {response.text}")

    #     # Get sales by agent
    #     response = requests.get(f"{sales_service_url}/sales/agent/{test_sale['agent_id']}")
    #     assert response.status_code == 200
    #     assert isinstance(response.json(), list)
        
    #     # Clean up
    #     requests.delete(f"{sales_service_url}/sales/{test_sale['sale_id']}")

    # def test_get_sales_by_branch(self, sales_service_url, test_sale):
    #     """Test retrieving sales by branch ID."""
    #     # First create a sale
    #     response = requests.post(
    #         f"{sales_service_url}/sales/",
    #         json=test_sale
    #     )
    #     initial_status = response.status_code
    #     if initial_status not in [200, 201, 409]:
    #         pytest.fail(f"Failed to create sale: {response.text}")

    #     # Get sales by branch
    #     response = requests.get(f"{sales_service_url}/sales/branch/{test_sale['branch_id']}")
    #     assert response.status_code == 200
    #     assert isinstance(response.json(), list)
        
    #     # Clean up
    #     requests.delete(f"{sales_service_url}/sales/{test_sale['sale_id']}")

    # def test_get_sales_by_team(self, sales_service_url, test_sale):
    #     """Test retrieving sales by team ID."""
    #     # First create a sale
    #     response = requests.post(
    #         f"{sales_service_url}/sales/",
    #         json=test_sale
    #     )
    #     initial_status = response.status_code
    #     if initial_status not in [200, 201, 409]:
    #         pytest.fail(f"Failed to create sale: {response.text}")

    #     # Get sales by team
    #     response = requests.get(f"{sales_service_url}/sales/team/{test_sale['team_id']}")
    #     assert response.status_code == 200
    #     assert isinstance(response.json(), list)
        
    #     # Clean up
    #     requests.delete(f"{sales_service_url}/sales/{test_sale['sale_id']}")

    def test_get_nonexistent_sale(self, sales_service_url):
        """Test retrieving a non-existent sale."""
        response = requests.get(f"{sales_service_url}/sales/nonexistent-sale")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_nonexistent_sale(self, sales_service_url, test_sale):
        """Test updating a non-existent sale."""
        updated_sale = test_sale.copy()
        updated_sale["sale_amount"] = 3000.0
        response = requests.put(
            f"{sales_service_url}/sales/nonexistent-sale",
            json=updated_sale
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_nonexistent_sale(self, sales_service_url):
        """Test deleting a non-existent sale."""
        response = requests.delete(f"{sales_service_url}/sales/nonexistent-sale")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower() 