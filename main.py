from quart import Quart
import asyncio
import api

api.app = Quart(__name__)

# Load config
config = api.classes.Config("config.yml")
api.config = config

asyncio.get_event_loop().run_until_complete(config.load())

# Create database
db = api.classes.Database()
api.db = db
asyncio.get_event_loop().run_until_complete(db.load())

# Load categories
for category in config.data:
    api.mem["ready"][category] = {
        "ready": False,
        "defaults": {},
        "last_ping": -1,
        "status": {}
    }

# Import blueprints
from blueprints import testcord

# Start
if __name__ == "__main__":
    api.app.run(
        port = 5555,
        debug = True
    )