# fastapi-mongo-crud-app
FastAPI MongoDB CRUD APP.
In this app, user can add products, fetch products with filter, and place the order

## SETUP - with Docker
### create .env file
copy all the data from .env.example to newly created .env

### Docker setup steps
1. Install and start the Dockers
2. In terminal, go to the project directory
3. run below command to create new network
    ```bash
    docker network create my-network
    ```
4. run command to create docker image of app
    ```bash
    docker build -t fastapi-mongo-crud .
    ```
5. after successful docker image creation run next command
    ```bash
    docker compose up
    ```
6. Now follow the documentation

## SETUP - Local Setup

### DB-SETUP
1. install the mongo-db in local
2. configure the mongo-uri in .env file
```bash
MONGO_URI="mongodb://localhost:27017"
```

### Create .env file
copy all the data from .env.example to newly created .env

### Create venv
```bash
python3.9 -m venv .venv
source .venv/bin/activate
```

### install all the requirements in venv
```bash
pip install -r requirements.txt --no-cache-dir
```

### start the server
```bash
uvicorn app.server:app --reload --port 9200
```

### Open the documentation after starting the server
1. http://localhost:9200/docs
2. http://localhost:9200/redocs


## Documentation

### POST /create
#### Sample Body
```bash
{
    "name": "coffee maker",
    "price": 4999.0,
    "quantity": 15
}
```

#### Sample Response
```bash
{
    "success": true,
    "message": "document inserted successfully"
}
```

#### CURL
```bash
curl --location 'http://localhost:9200/create' \
--header 'Content-Type: application/json' \
--data '{
    "name": "coffee maker",
    "price": 4999.0,
    "quantity": 15
}'
```


### GET /products
#### Sample Response
```bash
{
    "success": true,
    "message": "documents fetched successfully",
    "data":
    {
        "data": [
            {
                "_id": "65bce24445bf41c2f53d392b",
                "name": "macbook",
                "price": 129000.0,
                "quantity": 8
            }
        ],
        "page":
        {
            "limit": 10,
            "nextOffset": null,
            "prevOffset": null,
            "total": 1
        }
    }
}
```

#### Sample Response
```bash
{
    "success": true,
    "message": "order created successfully",
    "data":
    {
        "total_bill_amount": 273996.0
    }
}
```

#### CURL
```bash
curl --location 'http://localhost:9200/products?limit=10&offset=0&min_price=100000&max_price=200000'
```


### POST /order
#### Sample Body
```bash
{
    "items": [
        {
            "product_id": "65bce24445bf41c2f53d392b",
            "bought_quantity": 2
        },
        {
            "product_id": "65bce26e45bf41c2f53d392c",
            "bought_quantity": 4
        }
    ],
    "city": "ghaziabad",
    "country": "india",
    "zipcode": "201014"
}
```

#### CURL
```bash
curl --location 'localhost:9200/order' \
--header 'Content-Type: application/json' \
--data '{
    "items": [
        {
            "product_id": "65bce24445bf41c2f53d392b",
            "bought_quantity": 2
        },
        {
            "product_id": "65bce26e45bf41c2f53d392c",
            "bought_quantity": 4
        }
    ],
    "city": "ghaziabad",
    "country": "india",
    "zipcode": "201014"
}'
```
