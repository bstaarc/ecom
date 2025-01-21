import logging
import json
import psycopg2


def get_db_connection():
    try:
        with open("/ecom/config/db_creds.json", "r") as f:
            db_params = json.load(f)

        # Connect to the PostgreSQL database
        connection = psycopg2.connect(**db_params)
        return connection
    except Exception as e:
        logging.error("Error: Failed to create database object- {}".format(e))


def insert_demo_data():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Adding demo products
        insert_data = []
        product_dict = {"name": "Sofa",
                        "description": "Description for a Sofa",
                        "price": 24500.0, "stock": 128}
        insert_data.append(product_dict)
        product_dict = {"name": "Bed",
                        "description": "Description for a Bed",
                        "price": 45000.0, "stock": 230}
        insert_data.append(product_dict)
        product_dict = {"name": "Dining Table",
                        "description": "Description for a Dining Table",
                        "price": 12200.5, "stock": 45}
        insert_data.append(product_dict)
        product_dict = {"name": "Chair",
                        "description": "Description for a Chair",
                        "price": 4500.0, "stock": 300}
        insert_data.append(product_dict)

        for i in insert_data:
            try:
                query = "insert into product (name, description, price, stock)" \
                        " values (%(name)s, %(description)s, %(price)s, %(stock)s) ON CONFLICT (name) DO NOTHING"
                cursor.execute(query, i)
            except Exception as e:
                logging.error(f"Failed to add demo product with name - {i['name']} - {e}")
        logging.info("Demo product data inserted successfully")

        # Adding demo orders
        insert_data = []
        order_dict = {"products": [{"product_id": 1, "quantity": 2}, {"product_id": 3, "quantity": 5}],
                      "total_price": 110002.5, "status": "pending"}
        insert_data.append(order_dict)
        order_dict = {"products": [{"product_id": 3, "quantity": 6}, {"product_id": 4, "quantity": 10}],
                      "total_price": 118203.0, "status": "completed"}
        insert_data.append(order_dict)
        order_dict = {"products": [{"product_id": 2, "quantity": 1}],
                      "total_price": 45000.0, "status": "pending"}
        insert_data.append(order_dict)

        for i in insert_data:
            try:
                summary_details = []
                for product in i["products"]:
                    summary_details.append(json.dumps(product))
                i["products"] = summary_details
                query = "insert into order_table (products, total_price, status)" \
                        " values (%(products)s::json[], %(total_price)s, %(status)s)"
                cursor.execute(query, i)
            except Exception as e:
                logging.error(f"Failed to add demo order with products - {i['products']} - {e}")
            logging.info("Demo order data inserted successfully")

        connection.commit()

        return True
    except Exception as e:
        logging.error("Error: Failed to insert Demo data- {}".format(e))
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def initialize_tables():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # table_name: product
        create_product_table = 'CREATE TABLE IF NOT EXISTS product (id SERIAL primary key, ' \
                               'name text, description text, price float, stock int, CONSTRAINT _unique_product_name UNIQUE (name))'

        # table_name: order
        create_order_table = '''CREATE TABLE IF NOT EXISTS order_table (id SERIAL primary key, ''' \
                             '''products json [], total_price float, status varchar(10) DEFAULT 'pending' CHECK (status IN ('pending', 'completed')))'''

        cursor.execute(create_product_table)
        cursor.execute(create_order_table)

        connection.commit()

        # add dummy data
        if insert_demo_data():
            logging.info("Demo product and order data added successfully")


    except Exception as e:
        logging.error("Error: Failed while initializing tables- {}".format(e))
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == '__main__':
    initialize_tables()
