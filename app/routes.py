from fastapi.params import Depends
from fastapi.routing import APIRouter

from app.context import app_context
from app.request_validations import createProduct, fetchProduct, placeOrder
from app.service import *
from app.utils import generate_response, get_logger

router = APIRouter()

logger = get_logger()
LOGGER_KEY = "app.routes"


@router.get("/public/healthz")
async def _get_health_check():
    return "OK"


@router.post("/create")
async def create_product(data: createProduct):
    """
    API to create a product
    """
    logger.info(f"{LOGGER_KEY}.create_product")
    payload = data.model_dump()

    # check if document with same name already exists
    payload["name"] = payload["name"].lower()
    existing_records = await fetch_product_by_name(payload["name"])
    if existing_records.get("error"):
        return generate_response(message=existing_records["error"], success=False, code=existing_records["status_code"])

    # return bad_request if same product already exists
    if existing_records.get("data"):
        return generate_response(
            message="product with same name already exists", success=False, code=HTTPStatus.BAD_REQUEST.value
        )

    # insert new record into DB
    insert_response = await insert_product(payload)
    if insert_response.get("error"):
        return generate_response(message=insert_response["error"], success=False, code=insert_response["status_code"])

    # returning success response
    return generate_response(message="document inserted successfully", success=True, code=HTTPStatus.CREATED.value)


@router.get("/products")
async def fetch_products(query_args: fetchProduct = Depends()):
    """
    API to fetch the product with filters(Optional)
    """
    logger.info(f"{LOGGER_KEY}.fetch_products")
    query_args = query_args.model_dump()

    # fetch products based on the filters if provided
    fetch_response = await fetch_product_by_filter(query_args)
    if fetch_response.get("error"):
        return generate_response(message=fetch_response["error"], success=False, code=fetch_response["status_code"])

    return generate_response(
        message="documents fetched successfully", success=True, code=HTTPStatus.OK.value, data=fetch_response["data"]
    )


@router.post("/order")
async def place_order(data: placeOrder):
    """
    API to place the order
    """
    logger.info(f"{LOGGER_KEY}.place_order")
    payload = data.model_dump()

    # create the order and update the quantity of the products
    order_response = await process_order(payload)
    if order_response.get("error"):
        return generate_response(message=order_response["error"], success=False, code=order_response["status_code"])

    return generate_response(
        message="order created successfully", success=True, code=HTTPStatus.CREATED.value, data=order_response["data"]
    )
