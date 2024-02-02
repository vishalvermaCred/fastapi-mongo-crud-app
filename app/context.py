from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from data.mongo import MongoDB


class AppContext:
    db: Optional[MongoDB]


app_context = AppContext()
