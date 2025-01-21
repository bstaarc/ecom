import unittest
import json
import sys
sys.path.append('/usr/ecom-v1')
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_restx import Api
from api_service.orders import api

app = Flask(__name__)
api_instance = Api(app)
api_instance.add_namespace(api, path='/mgmt')

client = app.test_client()

class TestOrderEndpoints(unittest.TestCase):

    @patch('api_service.orders.get_db_connection')
    def test_post_order_success(self, mock_db_conn):
        mock_cursor = MagicMock()
        #mock_cursor.fetchone.side_effect = [(10,), (20,)]
        #mock_db_conn.return_value.cursor.return_value = mock_cursor

        data = {
                "products": [{"product_id": 1, "quantity": 2}, {"product_id": 3, "quantity": 5}],
                "total_price": 110002.5,
                "status": "pending"
            }
        response = client.post('/mgmt/orders', json=data)
        print(response.text)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], "SUCCESS")



    @patch('api_service.orders.get_db_connection')
    def test_post_order_missing_products_key(self, mock_db_conn):
        data = {
            "order": {
                "total_price": 110002.5,
                "status": "pending"
            }
        }
        response = client.post('/mgmt/orders', json=data)
        print(response.text)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.text)['message'], "Input payload validation failed")

    @patch('api_service.orders.get_db_connection')
    def test_post_order_price_as_string(self, mock_db_conn):
        data = {
            "order": {
                "products": [{"product_id": 1, "quantity": 2}],
                "total_price": "invalid_price",
                "status": "pending"
            }
        }
        response = client.post('/mgmt/orders', json=data)
        print(response.text)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.text)['message'], "Input payload validation failed")

if __name__ == '__main__':
    unittest.main()
