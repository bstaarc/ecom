# eCom Project

## Clone the Repository
Clone the repository using the following command:
```bash
git clone https://github.com/bstaarc/ecom.git
```

## Running the Application with Docker Compose

1. Locate the `docker-compose.yml` file in the `ecom` folder.
2. Run the following command to start the application:
    ```bash
    docker-compose up -d
    ```
3. To view the logs, use:
    ```bash
    docker-compose logs -f
    ```

## Testing the API Endpoints

### Using Swagger
Access the Swagger UI to test the API endpoints:
```text
Go to http://127.0.0.1:8086
```

### Using Postman
Find the Postman collection attached in the email for testing the API endpoints.

## Running the Test Scripts

1. Access the container:
    ```bash
    docker exec -it ecom-v1 /bin/bash
    ```
2. Run the following test scripts inside the container:
    ```bash
    python3 /usr/ecom-v1/scripts/test_products.py
    python3 /usr/ecom-v1/scripts/test_orders.py
    ```


