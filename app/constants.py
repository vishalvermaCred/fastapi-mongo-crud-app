from enum import Enum

PAGE_SIZE = 10

DB_NAME = "product_db"


class ResponseKeys:
    DATA = "data"
    SUCCESS = "success"
    MESSAGE = "message"


class Collections(Enum):
    PRODUCTS = "products"
    ORDERS = "orders"
