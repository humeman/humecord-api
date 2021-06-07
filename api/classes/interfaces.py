import os
import aiofiles
import json
import copy

import api
from ..utils import subprocess

class JSONInterface:
    def __init__(
            self,
            parent
        ):

        self.parent = parent

        self.files = {}

        self.data = {}

        self.lock = {}

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
    
    async def write(
            self,
            category: str
        ):
        if self.lock[category]:
            print(f"{category} is locked, skipping")
            return

        self.lock[category] = True

        path = self.files[category]["path"]

        async with aiofiles.open(f"{path}/db.json", mode = "w+") as f:
            await f.write(json.dumps(self.data[category], indent = 4))

        self.lock[category] = False

interfaces = {
    "json": JSONInterface
}