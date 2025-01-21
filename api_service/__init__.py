from api_service.products import api as products_api
from api_service.orders import api as orders_api

from flask_restx import Api


api = Api(version="1.0", title="ECOM Mgmt APIs", description="ECOM Mgmt API service")

api.add_namespace(products_api)
api.add_namespace(orders_api)