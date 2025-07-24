from datetime import datetime
class OrderPicker:
    CATEGORY_PRIORITY = {'perishable':0,'non_perishable':1}
    def __init__(self,orders,inventory):
        if not  isinstance(orders,list):
            raise ValueError('Orders must be a list')
        if not isinstance(inventory,dict):
            raise ValueError('inventory must be a dictionary with item quantities')
        self.orders = orders
        self.inventory = inventory
         
    def submit_order(self,order):
        required_field = ['item','quantity','category','timestamp']
        missing = [f for f in required_field if f not in order]
        if missing:
            raise ValueError(f"Missing field:{','.join(missing)}")
        self.orders.append(order)
        
    def next_order(self):
        available_order = [o for o in self.orders if self.inventory.get(o['item'],0) >= o['quantity'] ]
        sorted_order = sorted(available_order,key=lambda o : (self.CATEGORY_PRIORITY.get(o['category'],0) , o['timestamp']))
        next_order = sorted_order[0]
        self.inventory[next_order['item']] -= next_order['quantity']
        return next_order