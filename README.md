📦 Warehouse Order Fulfillment API
Efficient backend service for managing and fulfilling warehouse orders based on real-world constraints like stock availability, order urgency, and submission time. Built with Python, Flask, and designed for Dockerized deployment.

🚀 Features
✅ Add orders with stock quantity, urgency (category), and timestamp

📤 Retrieve next fulfillable order based on:

Availability

Urgency (perishable first)

Oldest order priority

📊 Dynamic inventory tracking as orders are fulfilled

🧪 Unit-tested with pytest and Flask client

🐳 Docker-ready for containerized deployment

🛠️ Tech Stack
Technology	Purpose
Flask	RESTful API
Python	Core backend logic & data structures
Docker	Containerization for deployment
Pytest	Testing framework
🔧 Installation
Clone the repo and install dependencies:

bash
git clone https://github.com/yourusername/warehouse-order-api.git
cd warehouse-order-api
pip install -r requirements.txt
🐳 Run with Docker
Build and start the container:

bash
docker build -t warehouse-api .
docker run -p 5000:5000 warehouse-api
📮 API Endpoints
POST /add_order
Submit a new order.

Request Body:

json
{
  "item": "milk",
  "quantity": 2,
  "category": "perishable",
  "timestamp": "2025-07-24T10:00:00Z"
}
GET /next_order
Returns the next fulfillable order and updates inventory.

GET /inventory
Returns current inventory levels.

🧠 Order Fulfillment Logic
Orders are picked based on this priority:

Only if stock is available

Perishable before non-perishable

Oldest first (timestamp)

📄 Testing
Run unit tests with:

bash
pytest
Test cases cover:

Field validation

Inventory updates

Order sorting logic

Edge cases like empty queue or insufficient stock

📚 License
This project is licensed under the MIT License.



