from contextlib import asynccontextmanager
from fastapi import FastAPI

from data.mongo import MongoDB
from app.context import app_context
from app.routes import router
from app.settings import BASE_ROUTE, MongoConfigs
from app.utils import get_logger

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_context.db = await _init_db(MongoConfigs)
    logger.info("🟢 DB initialized")
    await _init_routers()
    logger.info("🟢 routers initialized")
    yield
    await app_context.db.close()
    logger.info("🟢 DB connection closed")


app = FastAPI(lifespan=lifespan, docs_url=f"{BASE_ROUTE}/docs", redoc_url=f"{BASE_ROUTE}/redoc", redirect_slashes=False)


async def _init_db(configs):
    database = MongoDB(**configs)
    await database.connect()
    return database


async def _init_routers():
    app.include_router(router, prefix=BASE_ROUTE)
