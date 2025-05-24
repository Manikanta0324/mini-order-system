from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
app = FastAPI()
class OrderRequestModel(BaseModel):
    customer_name: str  
    item_name: str  
    quantity: int
    price_per_item: float
    @field_validator("quantity")
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than zero")
        return v

    @field_validator("price_per_item")
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price per item must be greater than zero")
        return v

class OrderStatusUpdateModel(BaseModel):
    status: str

    @field_validator("status")
    def status_must_be_valid(cls, v):
        valid_statuses = ["pending", "shipped", "delivered", "cancelled"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v
orders = {}
order_id_counter = 1
@app.post("/orders")
def create_order(order: OrderRequestModel):
    global order_id_counter
    new_order = order.dict()
    new_order['id'] = order_id_counter
    new_order['status'] = "pending"
    orders[order_id_counter] = new_order
    order_id_counter += 1
    return new_order

@app.get("/orders")
def get_all_orders():
    return list(orders.values())

@app.get("/orders/summary")
def get_summary():
    total_orders = len(orders)
    total_value = sum(order['quantity'] * order['price_per_item'] for order in orders.values())
    return {
        "total_orders": total_orders,
        "total_value": total_value
    }

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/orders/{order_id}")
def update_order(order_id: int, order_update: OrderStatusUpdateModel):
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order['status'] = order_update.status
    return order

@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    del orders[order_id]
    return {"detail": "Order deleted successfully"}


@app.get("/customers/{customer_name}")
def get_orders_by_customer(customer_name: str):
    customer_orders = [order for order in orders.values() if order['customer_name'].lower() == customer_name.lower()]
    if not customer_orders:
        raise HTTPException(status_code=404, detail=f"No orders found for customer '{customer_name}'")
    return customer_orders
