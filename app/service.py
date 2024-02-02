from bson import ObjectId
from http import HTTPStatus
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.utils import get_logger
from app.context import app_context
from app.constants import PAGE_SIZE, Collections

logger = get_logger()
LOGGER_KEY = "app.service"


async def fetch_product_by_name(product_name):
    """
    check if product with given name exists or not
    """
    logger.info(f"{LOGGER_KEY}.fetch_product_by_name")
    response = {"error": None, "status_code": None}
    try:
        data = await app_context.db.get_document_by_key(Collections.PRODUCTS.value, "name", product_name)
        response["data"] = data
    except Exception as e:
        logger.error(f"{LOGGER_KEY}.fetch_product_by_name.error: {str(e)}")
        response["error"] = str(e)
        response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
    return response


async def insert_product(document_data):
    """
    insert the document into products table
    """
    logger.info(f"{LOGGER_KEY}.insert_product")
    response = {"error": None, "status_code": None}
    try:
        doc_id = await app_context.db.insert_document(Collections.PRODUCTS.value, document_data)
        logger.info(f"{LOGGER_KEY}.insert_product.inserted_doc_id: {doc_id}")
    except Exception as e:
        logger.error(f"{LOGGER_KEY}.insert_product.exception: {str(e)}")
        response["error"] = str(e)
        response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
    return response


async def fetch_product_by_filter(query_args):
    """
    fetch all the products based on filter provided
    """
    logger.info(f"{LOGGER_KEY}.fetch_product_by_filter")
    response = {"error": None, "status_code": None}
    try:
        page_number = query_args.pop("page_number", 1)
        min_price = query_args.pop("min_price", None)
        max_price = query_args.pop("max_price", None)
        name = query_args.pop("name", None)
        offset = query_args.pop("offset", None)
        limit = query_args.pop("limit", None)
        document_id = query_args.pop("id", None)

        # calculating the offset
        if offset is None:
            offset = (page_number - 1) * PAGE_SIZE

        if limit is None:
            limit = PAGE_SIZE

        # aggregation pipeline
        price_filter = {}
        if min_price:
            price_filter["$gte"] = min_price
        if max_price:
            price_filter["$lte"] = max_price

        pipeline = [
            {
                "$match": {
                    "_id": {"$eq": ObjectId(document_id)} if document_id is not None else {"$exists": True},
                    "name": {"$eq": name.lower()} if name is not None else {"$exists": True},
                    "price": price_filter if price_filter else {"$exists": True},
                }
            },
            {"$facet": {"data": [{"$skip": offset}, {"$limit": limit}], "total": [{"$count": "count"}]}},
            {"$unwind": "$total"},  # Unwind the total array to get a single document
        ]
        print(f"\n\n pipeline: {pipeline} \n\n")
        documents = await app_context.db.get_documents_using_aggregation(Collections.PRODUCTS.value, pipeline)

        if documents:
            # Extract data and total count from the result
            data = documents[0]["data"]
            data = [app_context.db._convert_id_to_str(doc) for doc in data]
            total_count = documents[0]["total"]["count"]
        else:
            total_count, data = 0, {}

        # Calculate nextOffset and prevOffset
        next_offset = total_count - (offset + limit) if total_count - (offset + limit) > 0 else None
        prev_offset = offset if offset > 0 else None

        # Prepare metadata information
        page_info = {"limit": limit, "nextOffset": next_offset, "prevOffset": prev_offset, "total": total_count}

        # Prepare the final response
        data = {"data": data, "page": page_info}
        response["data"] = data
    except Exception as e:
        logger.error(f"{LOGGER_KEY}.fetch_product_by_filter.exception: {str(e)}")
        response["error"] = str(e)
        response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
    return response


async def get_documents_using_ids(items):
    """
    fetch the documents whole id is provided by user
    """
    logger.info(f"{LOGGER_KEY}.get_documents_using_ids")
    product_ids = list(items.keys())
    product_ids = [ObjectId(product_id) for product_id in product_ids]
    pipeline = [{"$match": {"_id": {"$in": product_ids}}}]
    documents = await app_context.db.get_documents_using_aggregation(Collections.PRODUCTS.value, pipeline)
    return documents


async def get_total_amount(documents, items):
    """
    get the total amount of the order
    """
    logger.info(f"{LOGGER_KEY}.get_total_amount")
    total_price = 0
    for document in documents:
        product_id = document["_id"]
        price = document["price"]
        total_price += price * items[product_id]
    return total_price


async def get_formatted_product_list(items):
    """
    formats the items to a dict of product_id to quantity
    """
    logger.info(f"{LOGGER_KEY}.get_formatted_product_list")
    formatted_items = {}
    for product_details in items:
        product_id = product_details["product_id"]
        quantity = product_details["bought_quantity"]
        formatted_items[product_id] = quantity
    return formatted_items


def get_order_place_query(total_amount, payload):
    """
    create the query for order
    """
    logger.info(f"{LOGGER_KEY}.get_order_place_query")
    items = payload.get("items")
    address = {"city": payload.get("city"), "country": payload.get("country"), "zipcode": payload.get("zipcode")}
    insert_query = {
        "items": items,
        "created_on": str(datetime.now()),
        "total_amount": total_amount,
        "user_address": address,
    }
    return insert_query


def get_products_update_query(formatted_items):
    """
    get the update query for product
    """
    logger.info(f"{LOGGER_KEY}.get_products_update_query")
    bulk_update_query = []
    for product_id, quantity in formatted_items.items():
        update_query = [
            {"_id": ObjectId(product_id), "quantity": {"$gte": quantity}},
            {"$inc": {"quantity": -quantity}},
        ]
        bulk_update_query.append(update_query)
    return bulk_update_query


async def insert_orders_and_update_products(order_place_query, products_update_query):
    """
    insert the order into orders table and update products table
    """
    logger.info(f"{LOGGER_KEY}.insert_orders_and_update_products")
    response = {"error": None, "status_code": None}
    try:
        async with await app_context.db.client.start_session() as session:
            order_id = await app_context.db.insert_document(Collections.ORDERS.value, order_place_query, session)
            logger.info(f"{LOGGER_KEY}.insert_orders.order_id: {order_id}")
            update_responses = []
            for update_query in products_update_query:
                update_response = await app_context.db.update_document(Collections.PRODUCTS.value, update_query)
                update_responses.append(update_response)
            logger.info(f"{LOGGER_KEY}.insert_orders.update_response: {all(update_responses)}")
    except Exception as e:
        logger.error(f"{LOGGER_KEY}.insert_orders.exception: {str(e)}")
        response["error"] = str(e)
        response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
    return response


async def process_order(payload):
    """
    process the order by formatting the data
    create the order into orders table
    update the products quantity
    """
    logger.info(f"{LOGGER_KEY}.process_order")
    response = {"error": None, "status_code": None}
    try:
        items = payload.get("items")
        formatted_items = await get_formatted_product_list(items)
        documents = await get_documents_using_ids(formatted_items)
        total_amount = await get_total_amount(documents, formatted_items)
        order_place_query = get_order_place_query(total_amount, payload)
        products_update_query = get_products_update_query(formatted_items)
        response = await insert_orders_and_update_products(order_place_query, products_update_query)
        if response.get("error"):
            return response
        # returning total bill amount in success response
        response["data"] = {"total_bill_amount": total_amount}
    except Exception as e:
        logger.error(f"{LOGGER_KEY}.process_order.exception: {str(e)}")
        response["error"] = str(e)
        response["status_code"] = HTTPStatus.INTERNAL_SERVER_ERROR.value
    return response
