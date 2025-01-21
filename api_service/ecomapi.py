import sys
from gevent import monkey
monkey.patch_all()
import logging
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

sys.path.append('/usr/ecom-v1')

from api_service import api


try:
    app = Flask(__name__)
    cors = CORS(app, expose_headers=["Content-Disposition"])
    app.wsgi_app = ProxyFix(app.wsgi_app)

    api.init_app(app)
except Exception as e:
    logging.error(e)


def execute():
    logging.info('Initializing Cluster api service')
    app.run(host="0.0.0.0", port=8086)


if __name__ == "__main__":
    execute()
