import aiofiles
import yaml

class Config:
    def __init__(
            self,
            path: str
        ):

        self.path = path

    async def load(
            self
        ):

        async with aiofiles.open(self.path, mode = "r") as f:
            self.raw = yaml.safe_load(await f.read())

        for key, value in self.raw.items():
            setattr(self, key, value)
