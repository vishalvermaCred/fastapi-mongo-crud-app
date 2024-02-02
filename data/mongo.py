from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Type, Any, Dict, List, Union


class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self.client: Optional[Type[Any]] = None
        self.db: Optional[Type[Any]] = None
        self.uri = uri
        self.db_name = db_name

    async def connect(self):
        self.client = AsyncIOMotorClient(self.uri)
        self.db = self.client[self.db_name]

    async def close(self):
        if self.client:
            self.client.close()

    def get_collection(self, collection_name: str):
        return self.db[collection_name]

    async def insert_document(self, collection_name: str, document: Dict[str, Any], session=None) -> ObjectId:
        collection = self.get_collection(collection_name)
        result = await collection.insert_one(document, session=session)
        return result.inserted_id

    async def get_document_by_key(self, collection_name: str, key: str, key_value: str) -> Optional[Dict[str, Any]]:
        collection = self.get_collection(collection_name)
        document = await collection.find_one({key: key_value})
        return document

    async def get_document_by_id(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        collection = self.get_collection(collection_name)
        document = await collection.find_one({"_id": ObjectId(document_id)})
        return document

    async def get_all_documents(self, collection_name: str) -> List[Dict[str, Any]]:
        collection = self.get_collection(collection_name)
        cursor = collection.find()
        documents = [self._convert_id_to_str(doc) for doc in await cursor.to_list(None)]
        return documents

    async def get_documents_using_aggregation(self, collection_name: str, pipeline: List):
        collection = self.get_collection(collection_name)

        # Execute the aggregation pipeline
        cursor = collection.aggregate(pipeline)

        # Convert result cursor to a list of documents
        documents = [self._convert_id_to_str(doc) for doc in await cursor.to_list(None)]
        return documents

    def _convert_id_to_str(self, document: Dict[str, Any]) -> Dict[str, Union[str, Any]]:
        """Convert ObjectId to string in document."""
        if "_id" in document:
            document["_id"] = str(document["_id"])
        return document

    async def update_document(self, collection_name: str, update_query: Dict[str, Any], session=None) -> bool:
        collection = self.get_collection(collection_name)
        result = await collection.update_one(update_query[0], update_query[1], session=session)
        return result.modified_count > 0

    async def bulk_update(self, collection_name: str, query: List, session=None) -> bool:
        collection = self.get_collection(collection_name)
        result = await collection.bulk_write(query)
        return result.modified_count > 0
