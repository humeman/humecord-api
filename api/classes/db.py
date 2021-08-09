import json

import api
from ..utils import exceptions
from ..utils import misc
from . import interfaces
import motor.motor_asyncio
from requests.utils import requote_uri
from typing import Optional
import asyncio
import pymongo

class JSONDatabase:
    def __init__(
            self
        ):
        self.interface = interfaces.interfaces["json"](self)

        self.interface.start()

    async def load(
            self
        ):

        await self.interface.load()

    async def get(
            self,
            category: str,
            path: str
        ):

        if category not in self.interface.data:
            raise exceptions.NotFound(f"Category {category} doesn't exist")

        return misc.follow(self.interface.data[category], path)

    async def put(
            self,
            category: str,
            path: str,
            new
        ):

        if category not in self.interface.data:
            raise exceptions.NotFound(f"Category {category} doesn't exist")

        comp = []
        for name in path.split("/"):
            if "'" in name or '"' in name:
                raise exceptions.SecurityError("Blocked attempt to escape string")

            comp.append(f"['{name}']")

        exec(f"self.interface.data['{category}']{''.join(comp)} = new")
        await self.interface.write(category)

class MongoDatabase:
    def __init__(
            self,
            parent
        ):

        self.parent = parent

    async def start(
            self
        ):

        self.write_concern = pymongo.write_concern.WriteConcern(w = 1)
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            "mongodb://{user}:{pass}@{host}:{port}".format_map(
                {
                    x: (requote_uri(y) if type(y) == str else y) for x, y in self.parent.config.mongo.items() if x in ["user", "pass", "host", "port"]
                }
            ),
            io_loop = asyncio.get_event_loop()
        )

        self.prefix = self.parent.config.mongo["db_prefix"]

        

    async def populate_defaults(
            self
        ):

        for database, collections in api.config.data.items():
            for collection, documents in collections.items():
                if type(documents) == dict:
                    for document, default in documents.items():
                        try:
                            await self.get(
                                database,
                                f"{collection}/{document}"
                            )

                        except exceptions.NotFound:
                            await self.put(
                                database,
                                f"{collection}/{document}",
                                default
                            )

                            print(f"Generated missing value: {database}/{collection}/{document}")

    async def get(
            self,
            database: str,
            path: str
        ):

        # We're looking for exactly 3 arguments here:
        # database/collection/document

        if path.count("/") < 1:
            raise Exception(f"Invalid path: '{path}' (must be formatted: collection/document)")

        collection, document = path.split("/", 1)

        ext = None

        if "/" in document:
            document, ext = document.split("/", 1)

        db = self.client[f"{self.prefix}{database}"]

        col = db.get_collection(collection, write_concern = self.write_concern)

        if ext is not None:
            arg_ext = []

        doc = await col.find_one({"_id": {"$eq": str(document)}})

        if doc is None:
            raise exceptions.NotFound(f"Document {document} doesn't exist")

        if ext is not None:
            # Follow into document
            return misc.follow(doc, ext.split("/")[1:])

        return doc

    async def put(
            self,
            database: str,
            path: str,
            new
        ):

        if path.count("/") < 1:
            raise Exception(f"Invalid path: '{path}' (must be formatted: database/collection/document)")

        collection, document = path.split("/", 1)

        ext = None

        if "/" in document:
            document, ext = path.split("/", 1)

        db = self.client[f"{self.prefix}{database}"]

        col = db.get_collection(collection, write_concern = self.write_concern)

        if ext is None:
            if type(new) != dict:
                raise exceptions.InvalidData("Data must be a dict to replace a document")

            result = await col.replace_one({"_id": {"$eq": document}}, new, upsert = True)

            if result.matched_count < 1 and (not result.upserted_id):
                raise exceptions.WriteFailed()

        else:
            ext_path = ext.strip("/").split("/")

            current = ext_path[0]
            
            doc = await col.find_one({"_id": {"$eq": document}})

            if doc is None:
                raise exceptions.NotFound(f"Document {document} doesn't exist")

            cur = doc[current]

            comp = []

            for name in ext_path[1:]:
                if "'" in name or '"' in name:
                    raise exceptions.SecurityError("Blocked attempt to escape string")

                comp.append(f"['{name}']")

            exec(f"cur{''.join(comp)} = new") # TODO: Find a better way to do this, this is kinda embarassing (especially for an API)
        
            result = await col.update_one({"_id": {"$eq": document}}, {"$set": {current: cur}})

            if result.matched_count < 1:
                raise exceptions.WriteFailed()

    async def update(
            self,
            database: str,
            path: str,
            changes: dict
        ):

        if path.count("/") < 1:
            raise Exception(f"Invalid path: '{path}' (must be formatted: collection/document)")

        collection, document = path.split("/", 1)

        db = self.client[f"{self.prefix}{database}"]

        col = db.get_collection(collection, write_concern = self.write_concern)

        result = await col.update_one({"_id": {"$eq": document}}, {"$set": {x: y for x, y in changes.items() if x != "_id"}}, upsert = True)

        if result.matched_count < 1 and (not result.upserted_id):
            raise exceptions.WriteFailed()

    async def list(
            self,
            database: str,
            collection: str,
            where: Optional[dict] = None,
            limit: int = 10000
        ):

        if "/" in collection:
            raise Exception(f"Invalid path: '{collection}' (list requires a collection only)")

        db = self.client[f"{self.prefix}{database}"]
        
        col = db.get_collection(collection, write_concern = self.write_concern)

        docs = col.find(where)

        doclist = await docs.to_list(length = limit)

        return {str(x["_id"]): x for x in doclist}