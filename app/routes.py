from flask import Flask,request,jsonify
from service import OrderPicker
from datetime import datetime
app = Flask(__name__)

initial_order  = []
inventory = {
    'apple': 29,
    'bread': 12,
    'Milk': 5
}
scheduled_manager_order = OrderPicker(initial_order,inventory)
@app.route('/add_order',methods=['POST'])
def add_order():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request Body must contain JSON data'}),400
        scheduled_manager_order.submit_order(data)
        return jsonify({'message':'order added successfully'}),201
    except ValueError as ve:
        return jsonify({'error':str(ve)}),400
    except Exception as e:
        print(f"unexpected error: {e}")
        return jsonify({'error':'An internal server error occurred.Please try again later'}),500
@app.route('/next_order', methods=['GET'])
def next_order():
    try:
        order = scheduled_manager_order.next_order()
        if order:
            return jsonify({'order_to_fulfill': order}), 200
        else:
            return jsonify({'message': 'No orders available or stock insufficient'}), 200
    except Exception as e:
        print(f"Error fetching next order: {e}")
        return jsonify({'error': 'An internal server error occurred.Please try again later '}), 500
