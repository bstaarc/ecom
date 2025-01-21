import unittest
import json
import sys
sys.path.append('/usr/ecom-v1')
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_restx import Api
from api_service.products import api

app = Flask(__name__)
api_instance = Api(app)
api_instance.add_namespace(api, path='/mgmt')

client = app.test_client()

class TestProductEndpoints(unittest.TestCase):

    @patch('api_service.products.get_db_connection')
    def test_get_products_success(self, mock_db_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, "Curtain", "A nice curtain", 1200.0, 70),
            (2, "Sofa", "A comfy sofa", 24500.0, 128)
        ]
        mock_cursor.description = [('id',), ('name',), ('description',), ('price',), ('stock',)]
        mock_db_conn.return_value.cursor.return_value = mock_cursor

        response = client.get('/mgmt/products?page=1&size=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], "SUCCESS")

    @patch('api_service.products.get_db_connection')
    def test_get_products_invalid_query_params_success(self, mock_db_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, "Curtain", "A nice curtain", 1200.0, 70),
            (2, "Sofa", "A comfy sofa", 24500.0, 128)
        ]
        mock_cursor.description = [('id',), ('name',), ('description',), ('price',), ('stock',)]
        mock_db_conn.return_value.cursor.return_value = mock_cursor

        response = client.get('/mgmt/products?abc=100&size=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], "SUCCESS")
        self.assertIsInstance(response.json['data'], list)

    @patch('api_service.products.get_db_connection')
    def test_get_products_out_of_range_page_no_success(self, mock_db_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, "Curtain", "A nice curtain", 1200.0, 70),
            (2, "Sofa", "A comfy sofa", 24500.0, 128)
        ]
        mock_cursor.description = [('id',), ('name',), ('description',), ('price',), ('stock',)]
        mock_db_conn.return_value.cursor.return_value = mock_cursor

        response = client.get('/mgmt/products?page=100&size=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], "SUCCESS")
        self.assertIsInstance(response.json['data'], list)

    @patch('api_service.products.get_db_connection')
    def test_get_products_empty_success(self, mock_db_conn):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [('id',), ('name',), ('description',), ('price',), ('stock',)]
        mock_db_conn.return_value.cursor.return_value = mock_cursor

        response = client.get('/mgmt/products?page=1&size=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], "SUCCESS")
        self.assertEqual(response.json['msg'], "No products to display")
        self.assertEqual(response.json['data'], [])

    @patch('api_service.products.get_db_connection')
    def test_post_products_success(self, mock_db_conn):
        mock_cursor = MagicMock()
        mock_db_conn.return_value.cursor.return_value = mock_cursor

        data = {
            "products": [
                {"name": "Curtain", "description": "A nice curtain", "price": 1200.0, "stock": 70},
                {"name": "Sofa", "description": "A comfy sofa", "price": 24500.0, "stock": 128}
            ]
        }
        response = client.post('/mgmt/products', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], "SUCCESS")

    @patch('api_service.products.get_db_connection')
    def test_post_products_duplicate_name(self, mock_db_conn):
        mock_cursor = MagicMock()
        mock_db_conn.return_value.cursor.return_value = mock_cursor

        data = {
            "products": [
                {"name": "Curtain", "description": "A nice curtain", "price": 1200.0, "stock": 70},
                {"name": "Curtain", "description": "Duplicate curtain", "price": 1300.0, "stock": 60}
            ]
        }
        response = client.post('/mgmt/products', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], "SUCCESS")

    @patch('api_service.products.get_db_connection')
    def test_post_products_invalid_json(self, mock_db_conn):
        response = client.post('/mgmt/products', json="Invalid json format")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.text).get("message"), "Input payload validation failed")

    def test_post_products_invalid_key(self):
        # Incorrect key 'products' instead of expected 'product'
        data = {
            "produts": [  # This should be 'product'
            {"name": "Curtain", "description": "A nice curtain", "price": 1200.0, "stock": 70},
            {"name": "Sofa", "description": "A comfy sofa", "price": 24500.0, "stock": 128}
            ]
        }
        response = client.post('/mgmt/products', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.text)['message'], "Input payload validation failed")

    def test_post_products_missing_description(self):
        data = {
            "product": [
            {"name": "Curtain", "price": 1200.0, "stock": 70},
            {"name": "Sofa", "description": "A comfy sofa", "price": 24500.0, "stock": 128}
            ]
        }
        response = client.post('/mgmt/products', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.text)['message'], "Input payload validation failed")

    def test_post_products_price_as_string(self):
        data = {
            "product": [
            {"name": "Curtain", "description": "A curtain", "price": "1200.0", "stock": 70},
            {"name": "Sofa", "description": "A comfy sofa", "price": "24500.0", "stock": 128}
            ]
        }
        response = client.post('/mgmt/products', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.text)['message'], "Input payload validation failed")


if __name__ == '__main__':
    unittest.main()
