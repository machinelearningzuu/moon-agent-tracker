import pytest
import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAgentService:
    """Tests for the Agent Service API."""

    def test_health_check(self, agent_service_url):
        """Test the health check endpoint."""
        response = requests.get(f"{agent_service_url}/agents/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["database"] == "connected"

    def test_get_all_agents(self, agent_service_url):
        """Test retrieving all agents."""
        response = requests.get(f"{agent_service_url}/agents/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    # def test_create_get_update_delete_agent(self, agent_service_url, test_agent):
    #     """Test the complete CRUD operations for an agent."""
    #     # Create agent
    #     response = requests.post(
    #         f"{agent_service_url}/agents/",
    #         json=test_agent
    #     )
    #     assert response.status_code in [200, 201, 409], f"Failed to create agent: {response.text}"
        
    #     if response.status_code == 409:
    #         logger.info("Agent already exists, continuing with test...")
    #     else:
    #         logger.info(f"Created agent: {response.json()}")
    #         assert response.json()["agent_id"] == test_agent["agent_id"]

    #     # Get agent
    #     response = requests.get(f"{agent_service_url}/agents/{test_agent['agent_id']}")
    #     assert response.status_code == 200
    #     assert response.json()["agent_id"] == test_agent["agent_id"]
    #     assert response.json()["name"] == test_agent["name"]

    #     # Update agent
    #     updated_agent = test_agent.copy()
    #     updated_agent["name"] = "Updated Test Agent"
    #     response = requests.put(
    #         f"{agent_service_url}/agents/{test_agent['agent_id']}",
    #         json=updated_agent
    #     )
    #     assert response.status_code == 200
    #     assert response.json()["name"] == "Updated Test Agent"

    #     # Delete agent
    #     response = requests.delete(f"{agent_service_url}/agents/{test_agent['agent_id']}")
    #     assert response.status_code == 200
    #     assert "deleted successfully" in response.json()["message"]

    #     # Verify deletion
    #     response = requests.get(f"{agent_service_url}/agents/{test_agent['agent_id']}")
    #     assert response.status_code == 404

    def test_get_nonexistent_agent(self, agent_service_url):
        """Test retrieving a non-existent agent."""
        response = requests.get(f"{agent_service_url}/agents/nonexistent-agent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    # def test_duplicate_agent_creation(self, agent_service_url, test_agent):
    #     """Test creating an agent with a duplicate ID."""
    #     # First create the agent
    #     response = requests.post(
    #         f"{agent_service_url}/agents/",
    #         json=test_agent
    #     )
    #     initial_status = response.status_code
        
    #     if initial_status in [200, 201]:
    #         # Now try to create it again
    #         response = requests.post(
    #             f"{agent_service_url}/agents/",
    #             json=test_agent
    #         )
    #         assert response.status_code == 409
    #         assert "already exists" in response.json()["detail"].lower()
            
    #         # Clean up
    #         requests.delete(f"{agent_service_url}/agents/{test_agent['agent_id']}")
    #     elif initial_status == 409:
    #         logger.info("Agent already exists, test passed")
    #     else:
    #         pytest.fail(f"Unexpected status code: {initial_status}")

    def test_update_nonexistent_agent(self, agent_service_url, test_agent):
        """Test updating a non-existent agent."""
        updated_agent = test_agent.copy()
        updated_agent["name"] = "This Should Fail"
        response = requests.put(
            f"{agent_service_url}/agents/nonexistent-agent",
            json=updated_agent
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_nonexistent_agent(self, agent_service_url):
        """Test deleting a non-existent agent."""
        response = requests.delete(f"{agent_service_url}/agents/nonexistent-agent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower() 