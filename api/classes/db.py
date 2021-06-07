import json

import api
from ..utils import exceptions
from ..utils import misc
from . import interfaces

class Database:
    def __init__(
            self,
            storage_type: str = "json"
        ):

        self.storage_type = storage_type

        # See if that interface exists
        if storage_type in interfaces.interfaces:
            self.interface = interfaces.interfaces[storage_type](self)

        else:
            raise exceptions.InvalidInterface()

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