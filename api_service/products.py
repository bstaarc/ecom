import sys
import json
import logging
import psycopg2

sys.path.append("/usr/ecom-v1")
from flask import request
from flask_restx import Resource, Namespace, fields

api = Namespace("mgmt/", description="Product related operations")
_product = api.model('product', {
    'name': fields.String(description='Name of the product', required=True),
    'description': fields.String(description='Description of the product', required=True),
    'price': fields.Float(description='Price of the product', min=0.0, required=True),
    'stock': fields.Integer(description='Stock of the product', min=0, required=True)
})

_products = api.model('products', {
    'products': fields.List(fields.Nested(_product), required=True)
})

def get_db_connection():
    try:
        with open("/ecom/config/db_creds.json", "r") as f:
            db_params = json.load(f)
        connection = psycopg2.connect(**db_params)
        return connection
    except Exception as e:
        logging.error("Error: Failed to create database object- {}".format(e))



@api.route("/products")
class Products(Resource):
    """
    GET - Listing all the available products
    POST - Adding new products
    """
    @api.doc(params={'page': 'page number', 'size': 'page size'})
    def get(self, **kwargs):
        """
        Listing all the available products
        params ?page=1&size=10
        """
        connection = None
        cursor = None
        try:
            pageno = int(request.args.get('page', 1))
            pagesize = int(request.args.get('size', 20))
            page_end = pagesize * pageno
            page_from = page_end - pagesize
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("select * from product")
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            res = [dict(zip(column_names, row)) for row in rows]

            if res:
                if page_end > len(res):
                    page_end = None
                elif page_from > len(res):
                    page_from = 0
                    page_end = None
                res = res[page_from:page_end]
                logging.info("Product list fetched successfully")
                return {"data": res, "status": "SUCCESS", "msg": "Product list fetched successfully", "status_code": 200}
            else:
                logging.info("No products to display")
                return {"data": res, "status": "SUCCESS", "msg": "No products to display", "status_code": 200}
        except Exception as e:
            logging.error(f"Failed to list products - {e}")
            return {"data": [], "status": "FAILED", "msg": "Failed to list products", "status_code": 400}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @api.expect(_products, validate=True)
    def post(self, **kwargs):
        """
        Adding products to the inventory
        payload
        {"products": [{"name": "Curtain", "description": "Description for a Curtain", "price": 1200.0, "stock": 70},
        {"name": "Sofa", "description": "Description for a Sofa", "price": 24500.0, "stock": 128},
        {"name": "Door", "description": "Description for a Door", "price": 13200.0, "stock": 25}]}
        """
        connection = None
        cursor = None
        try:
            data = request.json
            products = data["products"]
            connection = get_db_connection()
            cursor = connection.cursor()

            query = """INSERT INTO product (name, description, price, stock) VALUES (%s, %s, %s, %s) 
            ON CONFLICT (name) DO NOTHING"""
            values = [(product['name'], product['description'], product['price'], product['stock']) for product in
                      products]
            cursor.executemany(query, values)

            connection.commit()
            logging.info("Added all the products successfully")
            return {"data": [], "status": "SUCCESS", "msg": "Added all the products successfully", "status_code": 200}
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
