import os
import aiofiles
import json
import copy
import asyncio
import traceback

import api
from ..utils import subprocess

class JSONInterface:
    def __init__(
            self,
            parent
        ):

        self.task = None

        self.parent = parent

        self.files = {}

        self.data = {}

        self.lock = {}

        self.to_write = {}

    async def load(self):
        # Get all files from config
        for name, default_db in api.config.data.items():
            self.files[name] = {
                "path": f"db/{name}"
            }
            self.lock[name] = True

            if not os.path.exists(f"db/{name}"):
                # Create structure
                for command in [
                    f"mkdir db/{name}",
                    f"mkdir db/{name}/backups"
                ]:
                    await subprocess.run(command)

            # Try to read
            try:
                async with aiofiles.open(f"db/{name}/db.json", mode = "r") as f:
                    self.data[name] = json.loads(await f.read())

            except:
                # Generate
                async with aiofiles.open(f"db/{name}/db.json", mode = "w+") as f:
                    self.data[name] = copy.copy(default_db)
                    self.lock[name] = False
                    await self.write(name)

                #logger.log("error", f"JSON file {name} is invalid or corrupt.")
                #logger.traceback()
                #sys.exit(-1)

            self.lock[name] = False

    def start(
            self
        ):

        self.task = asyncio.get_event_loop().create_task(self.write_loop())

    async def watch(
            self
        ):

        while True:
            if self.task is not None:
                if self.task.done():
                    exc = self.task.exception()

                    if exc is not None:
                        try:
                            raise exc

                        except:
                            traceback.print_exc()

            await asyncio.sleep(1)

    async def write_loop(
            self
        ):

        print("WRITe loop")

        while True:
            await self.write_one()
            self.to_write = {}

            await asyncio.sleep(5)

    async def write_one(
            self
        ):
        print("Writing")

        for category, details in self.files.items():
            if self.to_write.get(category) == True:
                await self._write(category)

                path = details["path"]

                async with aiofiles.open(f"{path}/db.json", mode = "w+") as f:
                    await f.write(json.dumps(self.data[category], indent = 4))

                print(f"Wrote {category}")
    
    async def _write(
            self,
            category: str
        ):
        path = self.files[category]["path"]

        async with aiofiles.open(f"{path}/db.json", mode = "w+") as f:
            await f.write(json.dumps(self.data[category], indent = 4))

    async def write(
            self,
            category: str
        ):

        self.to_write[category] = True
        
        return

interfaces = {
    "json": JSONInterface
}
