import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import json

# Import your Flask app instance from run.py
# Assuming run.py has 'app = Flask(__name__)' and potentially other setup
from run import app 

# --- Fixture for Flask Test Client ---
@pytest.fixture
def client():
    """
    Configures the Flask app for testing and returns a test client.
    This client allows simulating HTTP requests to your Flask app.
    """
    app.config['TESTING'] = True # Puts Flask in testing mode, disabling error catching
    with app.test_client() as client:
        yield client

# --- Fixture for Mocking the OrderPicker Service ---
@pytest.fixture
def mock_order_picker():
    """
    Mocks the global 'scheduled_manager_order' instance in routes.py.
    This prevents tests from interacting with the real OrderPicker's in-memory state
    or any actual database connections, making tests faster and isolated.
    """
    # 'patch' replaces the actual object with a MagicMock during the test
    # 'routes.scheduled_manager_order' is the path to the specific instance you want to mock
    with patch('routes.scheduled_manager_order', new_callable=MagicMock) as mock_manager:
        yield mock_manager # Yield the mock object to the test function

# --- Test Cases for /add_order route ---

def test_add_order_success(client, mock_order_picker):
    """
    Tests a successful POST request to /add_order.
    Verifies the correct status code, response message,
    and that the service's submit_order method was called.
    """
    # Example order data that matches what your OrderPicker.submit_order expects
    # and what your JobModel requires (priority, estimated_time, timestamp, category, items)
    order_data_payload = {
        "id": "ORD001",
        "priority": 0, # Perishable
        "estimated_time": 60,
        "timestamp": datetime.utcnow().isoformat(), # Use ISO format for JSON compatibility
        "category": "Perishable",
        "items": [
            {"item_name": "apple", "quantity": 2},
            {"item_name": "bread", "quantity": 1}
        ]
    }
    
    # Simulate a POST request with JSON data
    response = client.post('/add_order', json=order_data_payload)
    
    # Assertions
    assert response.status_code == 201 # Expect 201 Created for successful addition
    assert response.json == {'message': 'order added successfully'}
    
    # Verify that the mocked service layer's submit_order method was called
    # and that it received the correct data from the request body
    mock_order_picker.submit_order.assert_called_once_with(order_data_payload)

def test_add_order_missing_json_body(client, mock_order_picker):
    """
    Tests a POST request to /add_order with an empty or invalid JSON payload.
    Verifies a 400 Bad Request and that the service method was NOT called.
    """
    # Simulate a POST request with an empty body
    response = client.post('/add_order', data="", content_type='application/json')
    
    # Assertions
    assert response.status_code == 400
    assert response.json == {'error': 'Request body must contain JSON data'}
    mock_order_picker.submit_order.assert_not_called() # Service should not be called if input is bad

def test_add_order_missing_required_fields_from_service(client, mock_order_picker):
    """
    Tests a POST request where the service layer (OrderPicker.submit_order)
    raises a ValueError due to missing required fields within the order data.
    """
    # This data is missing 'priority', which your OrderPicker.submit_order
    # (or JobModel's constructor) would validate and raise a ValueError for.
    invalid_order_data_payload = {
        "id": "ORD002",
        "estimated_time": 60,
        "timestamp": datetime.utcnow().isoformat(),
        "category": "Non-Perishable",
        "items": [
            {"item_name": "bread", "quantity": 1}
        ]
    }
    # Configure the mock service method to raise the expected ValueError
    mock_order_picker.submit_order.side_effect = ValueError("Missing required fields: priority")

    response = client.post('/add_order', json=invalid_order_data_payload)
    
    # Assertions
    assert response.status_code == 400 # Expect 400 Bad Request due to validation error
    assert response.json == {'error': 'Missing required fields: priority'}
    mock_order_picker.submit_order.assert_called_once_with(invalid_order_data_payload)

def test_add_order_internal_server_error(client, mock_order_picker):
    """
    Tests API handling of unexpected internal errors from the service layer
    during job submission.
    """
    # Simulate an unexpected error (e.g., database connection issue) from the service layer
    mock_order_picker.submit_order.side_effect = Exception("Simulated database connection failed")

    valid_order_data_payload = {
        "id": "ORD003",
        "priority": 1,
        "estimated_time": 30,
        "timestamp": datetime.utcnow().isoformat(),
        "category": "Perishable",
        "items": [
            {"item_name": "Milk", "quantity": 1}
        ]
    }
    response = client.post('/add_order', json=valid_order_data_payload)
    
    # Assertions
    assert response.status_code == 500 # Expect 500 Internal Server Error
    assert response.json == {'error': 'An internal server error occurred. Please try again later.'}
    mock_order_picker.submit_order.assert_called_once_with(valid_order_data_payload)

# --- Test Cases for /next_order route ---

def test_next_order_success(client, mock_order_picker):
    """
    Tests a successful GET request to /next_order when an order is available.
    Verifies the correct status code, response data, and service method call.
    """
    # Simulate the service returning a job dictionary (as your next_job() does)
    mock_order_to_fulfill = {
        "id": "ORD001-Fulfilled",
        "priority": 0,
        "estimated_time": 30,
        "timestamp": datetime.utcnow().isoformat(),
        "category": "Perishable",
        "items": [
            {"item_name": "apple", "quantity": 1}
        ]
    }
    mock_order_picker.next_order.return_value = mock_order_to_fulfill
    
    response = client.get('/next_order')
    
    # Assertions
    assert response.status_code == 200
    assert response.json == {'order_to_fulfill': mock_order_to_fulfill}
    mock_order_picker.next_order.assert_called_once()

def test_next_order_no_orders_available(client, mock_order_picker):
    """
    Tests a GET request to /next_order when no orders are available in the queue
    or stock is insufficient.
    """
    mock_order_picker.next_order.return_value = None # Simulate no order found
    
    response = client.get('/next_order')
    
    # Assertions
    assert response.status_code == 200 # As per your route's current logic
    assert response.json == {'message': 'No orders available or stock insufficient'}
    mock_order_picker.next_order.assert_called_once()

def test_next_order_internal_server_error(client, mock_order_picker):
    """
    Tests API handling of unexpected internal errors during next_order retrieval.
    """
    mock_order_picker.next_order.side_effect = Exception("Simulated database connection lost")
    
    response = client.get('/next_order')
    
    # Assertions
    assert response.status_code == 500
    assert response.json == {'error': 'An internal server error occurred. Please try again later.'}
    mock_order_picker.next_order.assert_called_once()