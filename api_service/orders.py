import sys
import json
import logging
import psycopg2

sys.path.append("/usr/ecom-v1")
from flask import request
from flask_restx import Resource, Namespace, fields

api = Namespace("mgmt/", description="Order related operations")

_product_in_order = api.model('product_in_order', {
    'product_id': fields.Integer(description='ID of the product', required=True),
    'quantity': fields.Integer(description='Quantity of the product', required=True)
})

_order = api.model('order', {
    'products': fields.List(fields.Nested(_product_in_order), description='Products in the order', required=True),
    'total_price': fields.Float(description='Total price of the order', required=True),
    'status': fields.String(
        description='Status of the order',
        required=False,
        default='pending',
        enum=['pending', 'completed']
    )
})


def get_db_connection():
    try:
        with open("/ecom/config/db_creds.json", "r") as f:
            db_params = json.load(f)
        connection = psycopg2.connect(**db_params)
        return connection
    except Exception as e:
        logging.error("Error: Failed to create database object- {}".format(e))



@api.route("/orders")
class Orders(Resource):
    """
    POST - Placing a new order
    """

    @api.expect(_order, validate=True)
    def post(self, **kwargs):
        """
        Placing a new order
        payload
        {"products": [{"product_id": 1, "quantity": 2}, {"product_id": 3, "quantity": 5}],
         "total_price": 110002.5, "status": "pending"}
        """
        connection = None
        cursor = None
        try:
            data = request.json
            order = data
            connection = get_db_connection()
            cursor = connection.cursor()
            order_reject_flag = False

            order_state = {"order_status": "SUCCESS", "reason": "Enough stock available",
                           "rejected_order_for": []}

            for product in order["products"]:
                try:
                    query = """SELECT stock FROM product WHERE id=%s AND stock>=%s FOR UPDATE"""
                    values = (product['product_id'], product['quantity'])
                    cursor.execute(query, values)
                    row = cursor.fetchone()

                    if row:
                        if order_reject_flag:
                            # Rollback since we don't intend to process this order just identifying and
                            # skipping products with enough stock from rejected_order_for list
                            continue
                        new_stock = row[0] - product['quantity']
                        query = """UPDATE product SET stock=%s WHERE id=%s"""
                        values = (new_stock, product['product_id'])
                        cursor.execute(query, values)
                    else:
                        connection.rollback()
                        order_state["order_status"] = "FAILED"
                        order_state["reason"] = "Not enough stock available"
                        order_state["rejected_order_for"].append(product)
                        order_reject_flag = True
                except Exception as e:
                    logging.error(f"Error while updating stock - {e}")
                    order_state["order_status"] = "FAILED"
            if order_state["order_status"] == "FAILED":
                connection.rollback()
                logging.warning(f"Failed to place an order - {order_state}")
                resp = {"data": order_state, "status": "FAILED", "msg": "Failed to place an order. Retry after adjusting your order.", "status_code": 200}
                return resp

            summary_details = []
            for product in order["products"]:
                summary_details.append(json.dumps(product))
            order["products"] = summary_details

            query = """INSERT INTO order_table (products, total_price, status) VALUES (%s::json[], %s, %s)"""
            values = (order['products'], order['total_price'], order['status'])
            cursor.execute(query, values)
            connection.commit()
            logging.info("Order placed successfully")
            return {"data": [], "status": "SUCCESS", "msg": "Order placed successfully", "status_code": 200}
        except json.JSONDecodeError as jde:
            logging.error(f"Invalid JSON data: {jde}")
            return {"data": [], "status": "FAILED", "msg": "Invalid JSON format", "status_code": 400}
        except Exception as e:
            logging.error(f"Failed to add products - {e}")
            if connection:
                connection.rollback()
            return {"data": [], "status": "FAILED", "msg": "Failed to list products", "status_code": 500}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
